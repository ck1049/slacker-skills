# V1.0 validation checklist

- Mode is explicit or assumption is visible.
- The matching official base or full-reference guide was read before prompt generation.
- Base modes use the ordered three-field structure; Ref2VA uses the ordered six-section structure.
- Subject identity and continuity anchors are concrete.
- Each shot has one primary action.
- Camera movement, subject movement, and timing do not contradict each other.
- Reference roles and labels follow the selected official mode; T2VA has no unresolved reference labels.
- Dialogue, sound, and music are separated from visual action.
- Rewrite sections are English; dialogue, lyrics, and visible text preserve their original language.
- Later shots use increasing `MM:SS.mmm` cut times within the requested duration.
- Prompt length is proportional to task complexity; no fixed word-count rule is applied.
- Hard constraints are distinguishable from stylistic preferences.
- Evidence labels are present for non-obvious rules.
