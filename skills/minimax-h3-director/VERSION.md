# Version 1.5.0

V1.0 is a usable, testable prompt-directing skill. It is not a claim that MiniMax publishes a single mandatory prompt grammar. Real video quality still requires generation tests and human evaluation.

V1.1 integrates MiniMax's official project-local `h3-prompt-writing` skill as the authoritative rewrite-format layer. It adds explicit T2VA/I2VA/FL2VA/L2VA/Ref2VA routing and corrects the earlier treatment of six-section Ref2VA output and reference labels.

V1.2 bundles exact snapshots of the official base-mode and Ref2VA guides inside this skill. A recipient can install or copy only `minimax-h3-director/` and retain the complete official prompt-writing rules without separately installing `h3-prompt-writing`.

V1.3 adds long-form adaptation. Stories and episodes longer than 15 seconds are planned as multiple independent 4–15 second H3 generation units, each with a complete official prompt, local timestamps, per-unit asset budgets, and explicit cross-unit continuity handoffs.

V1.4 separates operator-facing asset binding from model-facing prompt text. Each media-input unit now has a local label-to-file manifest, while the single paste-ready prompt block contains only official labels and no filenames or paths. Validation checks binding completeness, numbering, file types, unused assets, and path leakage.

V1.4.1 closes the fictional-asset loophole: media labels can be assigned only from a verified filesystem inventory, and validation now fails when a manifest target does not exist as a regular file.

V1.5 adds empty-project reference orchestration without coupling the Director to a particular generator. It preserves direct T2VA for simple tasks, distinguishes recommended from required references, emits capability-neutral asset requests, enforces authorization and cost boundaries, and binds only verified outputs.

Compared with the unavailable V0.1 baseline described in the handoff, this release makes evidence provenance explicit, separates official facts from inferences and community advice, adds validation and regression cases, and provides maintainable templates and update rules.
