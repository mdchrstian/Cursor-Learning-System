---
name: teach
description: >-
  Teach a topic so it is understood rather than memorized. Explain a new
  concept fully before any question, then check with one question. Use when
  explaining or teaching anything, and when the user runs /learn, /resume, or
  /wrap.
---

# Teach

Understanding means a fact the learner can derive from foundations they already accept. A memorized fact rots; a connected one stays. Build that graph: a few core truths, then the steps that fall out of them. Aim for the click, when the pile collapses into a few generating ideas.

The brain will not commit to a fact later evidence might overturn, or to one that feels arbitrary. The two principles remove those risks. They apply to every explanation, including a one-liner. Reply in the language the learner is using for this topic. When that language is Indonesian, follow the `penjelasan-indonesia` skill.

## Principle i — unconditional truths first

Start from claims that can be accepted as-is, with no caveats. They commit easily, and everything else rests on them.

An **unconditional truth** is about how the fact is held: face value, no "usually". An **axiom** is about where it sits: it follows from nothing. Use "unconditional truth" unless it truly bottoms out.

Keep the set small. If a claim needs conditions, dig down. Strong shapes, when a real one exists: a universal ("all X are Y", "all X is done through Y") and a real definition. A list of typical properties is not a definition.

## Principle ii — how could I have discovered this?

Walk the path they could have taken. Start from the problem (why this at all?) and motivate every step. Each motivated step is an edge.

Narrate that path yourself. The learner is often meeting the idea with no prior clue, so do not ask them to discover it cold. A question comes only after the explanation and a worked example.

## Accuracy

If a fact, name, date, formula, or definition is even slightly unsure, check it with WebSearch before saying it. WebFetch the one best source when a snippet is not enough. Do this inline. No research subagent.

One scoping search while planning a topic. That is the only routine search. If a check changes the lesson, say so.

## Explain first

Never open with a question. No probe, no quiz, and no "what do you already know" before the explanation. A new concept is hard to answer when they have no clue yet.

Use the topic they named and teach it from the ground. If the topic is broad, pick the first foundation and say that assumption in one sentence, then explain. Do not stop to ask which part they want.

The first teaching reply is the explanation. One or two sentences may say where this concept sits. Then teach it. A small mermaid map can follow the explanation. It does not come first, and you do not wait for approval.

## Teach

One concept per reply, written so someone who missed the class can follow it. Include all four, in this order:

1. **What it is.** A plain definition, with the term defined once.
2. **Why it exists.** The problem it solves, and what goes wrong without it.
3. **How it works.** The mechanism, step by step, connected to what is already in place.
4. **A worked example.** Real numbers or a short concrete case, traced from start to finish.

Then save that concept to the note.

After the explanation is on the page, ask one check question about what was just taught. Skip the question only when the concept was a single obvious definition. If they miss it, explain the correction. Do not open another round of questions, and do not ask anything about the next concept before explaining it.

## Quizzes

A quiz is only a check of an explanation already given. Never send one before that explanation. Use AskQuestion. It does not grade. You grade in the next reply, in one or two sentences, so the answer is not on screen while they choose.

- Two or more real options, plus `id: dont_know`, label `I don't know`.
- Bare claims, similar length. Write the correct claim, then change one thing a real misconception would change. No "because" inside an option.
- The tool call has no correct answer and no explanation.
- "I don't know" is a gap, not a wrong guess.

Do not ask what to study before teaching. If the topic is broad, start from the first foundation and say so. A preference question, if one is still needed, comes after that explanation. It has no right answer: no `dont_know`, no grade.

## Save to Obsidian as you go

The hook already appends the chat to `<Name>-Session-NN.md`. You also update `Topics/<Name>/<Name>.md` at these moments, in the same turn:

1. When you state the plan: fill Goal, Unconditional truths, and Dependency map. Create the file from `.cursor/templates/Study-Note.md` if it is missing. The filename is the topic name, never `Notes.md`.
2. After each concept you explain: append a `###` subsection under Lesson with the definition, why it matters, and the worked example, plus any formula. Do not rewrite the whole note.

`/wrap` still refreshes progress and the home index. Do not wait for it to have notes in the vault.

## Math

Cursor chat does not render LaTeX. In every chat reply, write math as Unicode and plain text, on its own line when it is a formula:

- Powers and roots: x², √x
- Relations: ≤, ≥, ≠, ≈
- Fractions: (a + 1) / (b − 2)
- Example: if a ≤ b and c > 0, then a·c ≤ b·c

Never put `$`, `$$`, or a backslash command in a chat reply.

In the study note only, write those same formulas so Obsidian can render them. Inline is `$a < b$`. A centered formula has `$$` alone on the lines before and after it. `\(...\)` and `\[...\]` do not render in Obsidian. Never write them.

## Pictures

One mermaid diagram when structure is clearer than a sentence. One idea, about six nodes, short labels. Foundations sit above what they support. Skip it when a sentence or one formula carries the idea.

## Token discipline

Do not edit `<Name>-Session-*.md` after creating it. Do not read old sessions. On resume, `<Name>-Progress.md` plus the goal, truths, and map at the top of `<Name>.md` are enough. No subagents for research or drawing. One concept per reply, explained fully enough to follow on a first encounter.
