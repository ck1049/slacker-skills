# Pricing verification

Pricing is time-sensitive. Before every paid plan, verify the current official Tripo OpenAPI pricing page or another official Tripo developer source. Do not rely on this file as a permanent price table.

Official sources:

- `https://docs.tripo3d.ai/get-started/pricing.html`
- `https://platform.tripo3d.ai/docs/billing`
- `https://developers.tripo3d.ai/`

As a fallback only, inspect the installed CLI documentation and recent account usage:

```powershell
tripo docs
tripo usage --json
tripo task list --limit 50 --json
```

At skill creation time (2026-08-01), official OpenAPI documentation listed these examples: H-series text-to-model 10 points without texture or 20 with texture; H-series image/multiview-to-model 20 without texture or 30 with texture; P1 text-to-model 30/40 and image/multiview-to-model 40/50; texture 10; rig check free; rig 25; retarget 10 per animation; conversion 5, with certain non-default conversion parameters adding 5. The published base conversion was USD 1 per 100 credits. These are snapshots for sanity checking, not authority.

When current official information conflicts with the snapshot, use the current official information and mention the date/source in the quote.
