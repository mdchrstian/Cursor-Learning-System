---
description: Save distilled notes and compact progress, then stop
---

Close this learning session. Do not edit any `<Name>-Session-*.md` file.

1. Update `Topics/<Name>/<Name>.md`. Keep this order: Goal, Unconditional truths, Dependency map (one mermaid DAG), Insights, Mistakes worth remembering. Merge with what is already there. The map stays small.
2. Rewrite `Topics/<Name>/<Name>-Progress.md` in this shape, one short line per bullet:

```markdown
---
topic:
updated:
last_session:
---

# <Name> Progress

- Goal:
- Mastered:
- Edge:
- Next:
- Gaps:
```

3. In `Home.md`, between `<!-- topics -->` and `<!-- /topics -->`, keep one bullet per topic: `- [[Topics/<Name>/<Name>|<Name>]] — session NN — YYYY-MM-DD`. Update this topic's line. Leave the other topics in place.
4. Reply with a short recap: what locked in, where the edge is, and the next node. Tell them to open a new chat and run `/resume <Name>` when they continue.
