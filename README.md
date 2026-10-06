# Cursor Learning System

A Cursor setup for learning something new with an AI tutor, and an Obsidian vault for the notes you want to reread. Adapted from [amosblomqvist/learn](https://github.com/amosblomqvist/learn), and trimmed so a lesson does not burn tokens on logging, diagrams, or a long quiz before any explanation.

The tutor explains a new concept first, in plain language, with one worked example. A single check question comes after that. The chat transcript is written by a local script, so saving notes does not cost extra tokens.

## What you need

- [Cursor](https://cursor.com)
- [Obsidian](https://obsidian.md)
- Python 3 available as `python3` on your PATH

## Set it up

1. Clone this repository and open the folder in Cursor.
2. Open the same folder as a vault in Obsidian.
3. Start a new Cursor chat and run `/learn your topic`.

Your notes appear in `Topics/<Topic>/`. Open `<Topic>.md` in Obsidian when you want rendered math. The filename is the topic name, so each note is its own node on the graph. The chat shows the same math as plain text (`x²`, `≤`), because Cursor does not render LaTeX.

## How a lesson goes

- `/learn <topic>` starts a topic, or adds another session if that topic already exists.
- The first reply explains. It says what the thing is, why it exists, how it works, and walks one example with real numbers.
- One check question comes after that explanation.
- Each concept is also appended to `<Topic>.md`, with formulas written as `$...$` or `$$` so Obsidian can render them.
- `/wrap` saves a short progress file. Do this about every 30–40 turns.
- `/resume <topic>` in a **new chat** continues from that progress file, without rereading old transcripts.

If you write in Indonesian, the explanation follows a direct style: the point first, a concrete example, and no filler.

## Your notes stay on your computer

`Topics/` and `.obsidian/` are gitignored. Cloning this repo gives someone the tutor setup, not your study notes. After you clone it, everything you learn stays in `Topics/` on your machine.

## Folder layout

| Path | What it is |
| --- | --- |
| `.cursor/rules/` | Always-on rules: explain first, write clearly, math format |
| `.cursor/skills/teach/` | How a lesson is taught |
| `.cursor/skills/penjelasan-indonesia/` | Style for Indonesian explanations |
| `.cursor/commands/` | `/learn`, `/resume`, `/wrap` |
| `.cursor/hooks/md_log.py` | Writes the chat into the session file |
| `.cursor/templates/` | Empty session and note templates |
| `Topics/<Name>/<Name>.md` | The study note. The filename is the topic, so the graph stays readable |
| `Topics/<Name>/` | Your private notes. Not part of the published repo |
| `Home.md` | Topic index inside the Obsidian vault |

## If the session file stays empty

Reload Cursor so it picks up the hook. Confirm `python3` runs in a terminal. The hook only starts logging after the tutor creates `Topics/<Name>/<Name>-Session-01.md`.
