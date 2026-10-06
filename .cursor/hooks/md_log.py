#!/usr/bin/env python3
"""Mirror a learning chat into Topics/<Name>/<Name>-Session-NN.md.

Cursor runs this on stdin JSON. It never blocks the agent: every path exits 0.
Unbound chats are ignored, except the latest prompt, which is flushed when a
session file is created (that prompt was sent before the file existed).
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import sys
import traceback
from pathlib import Path

SESSION_RE = re.compile(r"(?:^|/)Topics/[^/]+/[^/]+-Session-\d+\.md$")
MAX_BLOCK = 8000


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            data = {}
    except Exception:
        _log_error("parse", raw[:500])
        _emit({"continue": True})
        return 0

    event = str(data.get("hook_event_name") or "")
    try:
        if event == "afterFileEdit":
            on_file_edit(data)
        elif event == "beforeSubmitPrompt":
            on_prompt(data)
        elif event == "afterAgentResponse":
            on_response(data)
        elif event == "postToolUse":
            on_tool(data)
    except Exception:
        _log_error(event or "hook", traceback.format_exc())

    if event == "beforeSubmitPrompt":
        _emit({"continue": True})
    else:
        _emit({})
    return 0


def on_file_edit(data: dict) -> None:
    file_path = data.get("file_path")
    if not file_path:
        return
    path = resolve_path(data, str(file_path))
    root = workspace_root(data, path)
    if root is None or not _is_session(root, path):
        return
    conv = _conv_id(data)
    if not conv:
        return

    def bind(store: dict) -> None:
        rec = _record(store, conv)
        rec["file"] = str(path)
        # The opening prompt was sent before this file existed. Flush it only
        # once the file is actually on disk, so a failed write can retry.
        if not path.is_file():
            return
        prompt = rec.get("pending_prompt")
        if isinstance(prompt, str) and prompt.strip():
            append_block(path, marked("quote", "YOU", prompt))
            rec.pop("pending_prompt", None)

    _update(root, bind)


def on_prompt(data: dict) -> None:
    text = str(data.get("prompt") or "").strip()
    if not text:
        return
    conv = _conv_id(data)
    root = workspace_root(data)
    if not conv or root is None:
        return

    target: dict[str, str | None] = {"file": None}

    def stash_or_note(store: dict) -> None:
        rec = _record(store, conv)
        bound = rec.get("file")
        if isinstance(bound, str) and bound:
            target["file"] = bound
        else:
            rec["pending_prompt"] = text

    _update(root, stash_or_note)
    if target["file"]:
        append_block(Path(target["file"]), marked("quote", "YOU", text))


def on_response(data: dict) -> None:
    text = str(data.get("text") or "").strip()
    if not text:
        return
    _append_bound(data, marked("abstract", "TUTOR", text))


def on_tool(data: dict) -> None:
    name = str(data.get("tool_name") or "")
    if not re.search(r"AskQuestion", name, re.IGNORECASE):
        return
    block = format_ask(data.get("tool_input"), data.get("tool_output"))
    if block:
        _append_bound(data, block)


def _append_bound(data: dict, block: str) -> None:
    conv = _conv_id(data)
    root = workspace_root(data)
    if not conv or root is None:
        return
    target: dict[str, str | None] = {"file": None}

    def lookup(store: dict) -> None:
        rec = store.get("conversations", {}).get(conv) or {}
        bound = rec.get("file")
        if isinstance(bound, str) and bound:
            target["file"] = bound

    _update(root, lookup)
    if target["file"]:
        append_block(Path(target["file"]), block)


def format_ask(tool_input, tool_output) -> str:
    payload = coerce(tool_input)
    if not isinstance(payload, dict):
        payload = {}
    questions = payload.get("questions") or []
    if not isinstance(questions, list):
        questions = []

    by_id: dict[str, dict] = {}
    parts: list[str] = []
    title = str(payload.get("title") or "").strip()
    if title:
        parts.append(title)

    for index, question in enumerate(questions, 1):
        if not isinstance(question, dict):
            continue
        qid = str(question.get("id") or index)
        by_id[qid] = question
        prompt = str(question.get("prompt") or "").strip()
        lines = [f"{index}. {prompt}" if prompt else f"{index}."]
        options = question.get("options") or []
        if isinstance(options, list):
            for opt_i, option in enumerate(options, 1):
                if isinstance(option, dict):
                    label = option.get("label") or option.get("id") or ""
                else:
                    label = option
                lines.append(f"   {opt_i}. {label}")
        parts.append("\n".join(lines))

    question_body = "\n\n".join(p for p in parts if p.strip()) or "(question)"
    answer_body = format_answers(by_id, tool_output)
    return (
        callout("question", "Question", question_body)
        + "\n\n"
        + callout("example", "Answer", answer_body)
    )


def format_answers(by_id: dict[str, dict], tool_output) -> str:
    payload = coerce(tool_output)
    if payload is None or payload == "":
        return "(no answer)"
    if isinstance(payload, str):
        return payload.strip() or "(no answer)"
    if isinstance(payload, dict):
        inner = _unwrap_text(payload)
        if inner is not None:
            return inner
        answers = payload.get("answers", payload)
        lines = _answer_lines(by_id, answers)
        if lines:
            return "\n".join(lines)
        return _clip(json.dumps(payload, ensure_ascii=False, indent=2))
    if isinstance(payload, list):
        lines = _answer_lines(by_id, payload)
        if lines:
            return "\n".join(lines)
    return _clip(str(payload))


def _unwrap_text(payload: dict) -> str | None:
    for key in ("result", "output", "text", "content"):
        value = payload.get(key)
        if isinstance(value, str) and len(payload) == 1:
            return value.strip() or "(no answer)"
    return None


def _answer_lines(by_id: dict[str, dict], answers) -> list[str]:
    lines: list[str] = []
    if isinstance(answers, dict):
        # A map of question id -> selection, not an envelope we already failed to read.
        if "questions" in answers:
            return []
        for qid, answer in answers.items():
            if qid in ("title", "status"):
                continue
            question = by_id.get(str(qid))
            lines.append(f"{_question_label(question, str(qid))}: {_render_answer(question, answer)}")
        return lines
    if isinstance(answers, list):
        for item in answers:
            if not isinstance(item, dict):
                lines.append(_clip(str(item)))
                continue
            qid = str(item.get("questionId") or item.get("question_id") or item.get("id") or "")
            question = by_id.get(qid)
            label = _question_label(question, qid or "Answer")
            selected = (
                item.get("selectedOptionIds")
                or item.get("selected_option_ids")
                or item.get("selected")
                or item.get("value")
                or item.get("answer")
            )
            rendered = _render_answer(question, selected)
            note = item.get("freeformText") or item.get("other") or item.get("note")
            if note:
                rendered = f"{rendered} — {note}"
            lines.append(f"{label}: {rendered}")
    return lines


def _question_label(question: dict | None, qid: str) -> str:
    if question:
        prompt = str(question.get("prompt") or "").strip()
        if prompt:
            return prompt
    return qid or "Answer"


def _render_answer(question: dict | None, answer) -> str:
    if answer is None:
        return "(no answer)"
    if isinstance(answer, list):
        return ", ".join(_option_label(question, item) for item in answer)
    if isinstance(answer, dict):
        picked = answer.get("selectedOptionIds") or answer.get("id") or answer.get("label")
        if picked is not None:
            return _render_answer(question, picked)
        return _clip(json.dumps(answer, ensure_ascii=False))
    return _option_label(question, answer)


def _option_label(question: dict | None, value) -> str:
    text = str(value)
    options = (question or {}).get("options") or []
    if isinstance(options, list):
        for option in options:
            if isinstance(option, dict) and str(option.get("id")) == text:
                return str(option.get("label") or text)
    return text


def marked(kind: str, title: str, body: str) -> str:
    """Callout title, then normal Markdown.

    Lesson text stays outside the quote so Obsidian renders math and mermaid.
    """
    text = body.strip("\n")
    if len(text) > MAX_BLOCK:
        text = text[:MAX_BLOCK].rstrip() + "\n…"
    return f"> [!{kind}] {title}\n\n{text}"


def callout(kind: str, title: str, body: str) -> str:
    lines = [f"> [!{kind}] {title}", ">"]
    text = body.strip("\n")
    if len(text) > MAX_BLOCK:
        text = text[:MAX_BLOCK].rstrip() + "\n…"
    for line in text.splitlines() or [""]:
        lines.append(f"> {line}" if line else ">")
    return "\n".join(lines)


def append_block(path: Path, block: str) -> None:
    if not path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            handle.seek(0)
            existing = handle.read()
            stripped = block.strip()
            if stripped and stripped in existing[-max(len(stripped) + 20, 2000) :]:
                return
            handle.seek(0, os.SEEK_END)
            prefix = "\n\n" if handle.tell() > 0 else ""
            handle.write(prefix + block + "\n")
            handle.flush()
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def workspace_root(data: dict, file_path: Path | None = None) -> Path | None:
    roots = []
    for item in data.get("workspace_roots") or []:
        try:
            roots.append(Path(str(item)).resolve())
        except OSError:
            continue
    if file_path is not None:
        resolved = file_path.resolve()
        for root in roots:
            if resolved == root or root in resolved.parents:
                return root
        return None
    if roots:
        return roots[0]
    return Path(__file__).resolve().parents[2]


def resolve_path(data: dict, file_path: str) -> Path:
    path = Path(file_path)
    if path.is_absolute():
        return path
    cwd = data.get("cwd")
    if cwd:
        return Path(str(cwd)) / path
    root = workspace_root(data)
    if root is not None:
        return root / path
    return path


def _is_session(root: Path, path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return False
    return SESSION_RE.search(relative) is not None


def _conv_id(data: dict) -> str:
    return str(data.get("conversation_id") or "").strip()


def _record(store: dict, conv: str) -> dict:
    conversations = store.setdefault("conversations", {})
    rec = conversations.get(conv)
    if not isinstance(rec, dict):
        rec = {}
        conversations[conv] = rec
    return rec


def _update(root: Path, fn) -> None:
    directory = root / ".learning"
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / "bindings.lock"
    path = directory / "bindings.json"
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            store = _read_json(path)
            fn(store)
            _write_json(path, store)
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {"conversations": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"conversations": {}}
    if not isinstance(data, dict):
        return {"conversations": {}}
    if not isinstance(data.get("conversations"), dict):
        data["conversations"] = {}
    return data


def _write_json(path: Path, store: dict) -> None:
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def coerce(value):
    if isinstance(value, str):
        stripped = value.strip()
        if stripped[:1] in "{[":
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return value
    return value


def _clip(text: str) -> str:
    if len(text) <= MAX_BLOCK:
        return text
    return text[:MAX_BLOCK].rstrip() + "\n…"


def _log_error(event: str, detail: str) -> None:
    try:
        root = Path(__file__).resolve().parents[2]
        directory = root / ".learning"
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "hook.log").open("a", encoding="utf-8") as handle:
            handle.write(f"{event}: {detail}\n")
    except OSError:
        pass


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        _log_error("fatal", traceback.format_exc())
        _emit({"continue": True})
        sys.exit(0)
