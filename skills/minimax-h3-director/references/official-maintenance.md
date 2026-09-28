# Official freshness and compatibility

Before formal production or delivering executable prompts, consult the consuming project's official-check record. If it is missing, incomplete, or older than 24 hours, check official sources before claiming current compatibility. This also covers missed daily maintenance runs. Ordinary ideation can continue using the bundled snapshot.

Use `OFFICIAL_SOURCES.md` to locate the official H3 repository, its README specifications, `skills/h3-prompt-writing/SKILL.md`, and both reference guides. Check the actual target platform's official API documentation and deprecation notices separately: open-weight, hosted API, and Hub capabilities must not be treated as interchangeable. Follow successor links only when verified on an official source; do not switch the user's model automatically.

Compare against the last successful source commit and normalized content. Classify changes as editorial, additive, or compatibility-breaking. Adapt affected rules, templates, examples, and validators only on explicit official evidence. Preserve existing project model/version choices. Hub-specific skills are not portable dependencies. Never execute downloaded upstream scripts as part of a documentation check.

Record attempt time, per-source results and URLs, exact revision or content hash, affected rules, and validation results in the consuming project's maintenance record. Track source freshness separately from adaptation readiness. Advance `last_complete_success_at` only after all required sources were read and compared; a recent successful check does not imply pending adaptation is complete. No detected change is valid only after successful comparison.

For this maintenance repository, use `docs/official-monitor-state.json` and `docs/official-monitor-latest.md`. Installed copies use their own project's equivalent record; do not require access to the original author's absolute paths. Do not use a skill installation date or release date as a successful official check.

On unavailable official evidence, retain the last successful timestamp, report `official comparison unavailable`, and describe the affected scope. Drafts may continue against the pinned snapshot with that limitation; do not claim current execution compatibility. A confirmed breaking change affecting the selected mode must be resolved before labeling its output executable. Explicit user instructions to use a pinned version take precedence; disclose the version and unresolved compatibility limitation.

Validate adaptations with skill structural validation, relevant existing regression fixtures, and whitespace checks. Offline checks establish format and binding behavior, not rendered video quality. Actual generation, model downloads, paid calls, material uploads, and migration of existing works are outside routine maintenance.

Daily maintenance should notify only on meaningful official changes, completed adaptation, a new failed check, or required user action. Preserve unresolved failures without repeated identical notifications. Record no-change checks locally without creating date-only Git commits. Do not overwrite related user changes or force-push. Commit, publish, or synchronize only within the user's granted maintenance scope.
