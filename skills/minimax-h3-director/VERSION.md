# Version 1.2.0

V1.0 is a usable, testable prompt-directing skill. It is not a claim that MiniMax publishes a single mandatory prompt grammar. Real video quality still requires generation tests and human evaluation.

V1.1 integrates MiniMax's official project-local `h3-prompt-writing` skill as the authoritative rewrite-format layer. It adds explicit T2VA/I2VA/FL2VA/L2VA/Ref2VA routing and corrects the earlier treatment of six-section Ref2VA output and reference labels.

V1.2 bundles exact snapshots of the official base-mode and Ref2VA guides inside this skill. A recipient can install or copy only `minimax-h3-director/` and retain the complete official prompt-writing rules without separately installing `h3-prompt-writing`.

Compared with the unavailable V0.1 baseline described in the handoff, this release makes evidence provenance explicit, separates official facts from inferences and community advice, adds validation and regression cases, and provides maintainable templates and update rules.
