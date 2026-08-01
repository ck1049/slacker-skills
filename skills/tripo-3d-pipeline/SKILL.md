---
name: tripo-3d-pipeline
description: Plan, estimate, generate, process, animate, export, download, and organize 3D assets with the installed Tripo CLI. Use whenever the user asks to create or modify a Tripo model, including text/image/multiview-to-3D, refinement, texturing, retopology, segmentation, rigging, animation retargeting, GLB/FBX export, engine-ready assets, task queries, or credit-cost estimates. Always gather material requirements, show a preflight credit and currency estimate with current and projected balance, and obtain explicit approval before submitting any credit-consuming task.
---

# Tripo 3D Pipeline

Use `tripo` CLI as the primary interface. Avoid browser login unless CLI authentication is unavailable and the user approves browser use.

## Non-negotiable gate

Never submit a credit-consuming Tripo task until all of the following are complete:

1. Gather the material requirements.
2. Check the active profile and current balance with `tripo whoami --json` or `tripo balance --json`.
3. Verify current official task pricing when it may have changed. Read [references/pricing.md](references/pricing.md).
4. Present an itemized point estimate, currency estimate, current balance, and projected balance.
5. Ask for explicit approval of the quoted plan.

Treat approval as plan-specific. If inputs, candidate count, model version, texture quality, post-processing, animation count, or retry allowance changes materially, quote again and obtain fresh approval. Never interpret silence, an earlier general request, or approval of a different plan as permission to spend credits. Do not use `--yes` to bypass this human gate; it is allowed only after approval to bypass redundant CLI prompts.

Read-only queries, local file inspection, reference research, CLI help, downloads of already completed tasks, and free riggability checks do not require the spending gate unless they cause another external side effect.

## 1. Gather requirements

Inspect provided images/models first. Ask only for missing details that affect output, price, or technical viability. Cover as applicable:

- subject, style, proportions, and must-preserve features;
- source type: text, single image, 2-4 views, or existing model/task;
- target use: game engine, mobile/PC, film, AR/web, printing, animation, or toy;
- target engine and version, units, up-axis, pivot, and desired format;
- geometry: face/triangle budget, topology, separate parts, watertightness, LODs;
- materials: texture/PBR requirement, resolution, transparency, texture format;
- rig: humanoid, quadruped, creature, or none;
- animations: exact clip list, loop/root-motion requirements, frame-rate expectations;
- expressions: texture swaps, facial bones, or blendshapes; do not imply Tripo auto-rig creates facial blendshapes unless current documentation confirms it;
- candidate count, quality priority, deadline, and maximum point or currency budget;
- naming and output-directory convention.

Offer a sensible default when the user is unsure. State limitations early, especially facial expressions, custom keyframe animation, topology cleanup, and engine-side setup.

## 2. Build the plan without spending

Confirm CLI availability and capabilities with read-only commands such as:

```powershell
tripo --version
tripo doctor --json
tripo <group> <command> --help
```

Use `tripo ai --wizard` only for planning when it is guaranteed to stop for confirmation before submission. Otherwise compose deterministic `generate`, `model`, `anim`, `mesh`, and `task` commands yourself. Never probe behavior by submitting a paid task.

Validate chain legality locally before quoting. Prefer staged execution for risky workflows: generate candidates, review previews, then process only the selected winner.

## 3. Quote credits and currency

Provide three numbers when useful:

- **minimum**: one successful pass with no retries;
- **recommended**: realistic candidate/revision allowance;
- **hard cap**: maximum authorized spend; stop before exceeding it.

Itemize every paid step and quantity. Use this calculation:

```text
estimated_points = sum(unit_price * quantity)
projected_balance = current_balance - estimated_points
currency_cost = estimated_points / credits_per_currency_unit
```

Prefer the user's actual recent purchase ratio when provided. Otherwise use the current official base conversion and a current exchange rate, clearly labeled as an estimate. Separate free/promotional credits from replacement cash value. Do not claim an exact currency charge when payment fees, tax, regional pricing, subscriptions, or discounts are unknown.

Use this confirmation format:

```text
Plan: <summary>
Items: <task x quantity = points> ...
Minimum / recommended / hard cap: <points>
Currency estimate: <amount and conversion basis>
Current balance: <points>
Projected balance at approved cap: <points>
Free/local steps: <list>
Main risks or unsupported requirements: <list>
Proceed with this plan? No paid task will be submitted until you approve.
```

If the balance is insufficient, stop and explain the shortfall. Do not open top-up or billing pages unless asked.

## 4. Execute after approval

Record the approved plan and cap in the working notes. Execute the smallest useful stage first. Use `--json`, `--no-open`, explicit `--out`, and stable names where supported. Never expose API keys, signed artifact URLs, cookies, or authentication files.

After each paid stage:

1. Query the task result and actual `credits_consumed`.
2. Compare actual cumulative spend with estimate and cap.
3. Download and inspect artifacts and previews.
4. Stop for review before expensive downstream stages when quality is uncertain.
5. Re-quote and ask again before any unapproved retry, extra candidate, or expanded task.

Do not treat a successful API status as sufficient quality validation. Verify file existence, nonzero size, expected format/header, preview quality, and relevant engine constraints.

## 5. Organize deliverables

Default to a structure like:

```text
models/<project>/<asset>/<task-or-version>/
  source/
  model.glb
  model.fbx
  textures/
  animations/
  previews/
  task.json
```

Adapt to an existing repository taxonomy instead of imposing a new one. Preserve source assets and prior versions. Do not overwrite a working model without explicit approval.

## 6. Reconcile and report

At completion, report:

- task IDs and statuses;
- estimated versus actual points by stage;
- starting, actual ending, and CLI-confirmed current balance;
- estimated currency value and its conversion basis;
- output paths and formats;
- validation performed;
- known issues and recommended engine-side follow-up.

If a task fails, verify whether credits were refunded before reporting net cost. Do not retry automatically unless the approved plan explicitly included that retry and remains under the hard cap.
