---
name: alipay-mihoyo-analysis
description: >
  Analyze Alipay-exported transaction PDFs for MiHoYo/HoYoverse game purchases (Genshin Impact, Honkai: Star Rail).
  Use whenever the user asks to analyze 支付宝账单, check MiHoYo spending, summarize Genshin or Star Rail
  purchases, generate an expense report from payment PDFs, or understand their monthly card / battle pass
  spending patterns. Trigger this skill even if the user doesn't explicitly say "analysis" — any request
  involving Alipay PDFs and game purchases should use it.
---

# MiHoYo Alipay Bill Analysis

Extract all MiHoYo-related transactions from Alipay-exported PDF statements, automatically classify
them by game (Genshin Impact / Honkai: Star Rail) and purchase type, then produce a styled multi-sheet
Excel report.

## Prerequisites

The analysis script requires two Python libraries. Install them if not already available:

```bash
pip install pdfplumber openpyxl
```

## Running the analysis

Point the script at the directory containing your Alipay PDFs — it scans every `.pdf` file in that
directory automatically:

```bash
python .claude/skills/alipay-mihoyo-analysis/scripts/alipay_mihoyo_analysis.py "<PDF directory>"
```

If no directory is given, the current working directory is used.

### Important: PDF format

The PDFs must be **text-based transaction statements exported from the Alipay app**, not screenshots or
scanned images. If the PDF is password-protected, remove the password during export — the script cannot
decrypt locked files.

## What the output contains

The script produces `米哈游账单分析报告.xlsx` with five sheets:

| Sheet | Content |
|-------|---------|
| **年度汇总** | Year-by-year totals: transaction count, amount, split by Genshin vs Star Rail, percentage of grand total |
| **月卡统计** | Monthly pass (小月卡 ¥30) and battle pass (大月卡 ¥68/¥128) breakdown by year, product name, and game |
| **游戏分类明细** | Per-product breakdown for each game with counts and amounts, plus a side-by-side Genshin vs Star Rail comparison table |
| **全部交易明细** | Every transaction in chronological order, color-coded by game (green = Genshin, yellow = Star Rail), with auto-filter enabled |
| **总结** | Narrative summary with totals, yearly breakdown, and per-game/per-category statistics |

## How game recognition works

The script identifies the game by matching keywords in the product name. The counterparty is always
"上海米哈游影铁科技有限公司" (Shanghai MiHoYo Shadow Iron Technology Co., Ltd.).

### Genshin Impact (原神)

| Product keyword | Category |
|-----------------|----------|
| 空月祝福 | 小月卡 (¥30) |
| 珍珠纪行 | 大月卡 (¥68) |
| 珍珠之歌 | 大月卡 premium |
| 创世结晶 | 创世结晶 |

### Honkai: Star Rail (崩坏星穹铁道)

| Product keyword | Category |
|-----------------|----------|
| 列车补给凭证 | 小月卡 (¥30) |
| 无名客的荣勋/奖章 | 大月卡 (¥68/¥128) |
| 古老梦华 | 古老梦华 |
| 开拓助力礼包 | 礼包 |

Products without a matching keyword default to **原神**.

## Fallback for problematic PDFs

If `pdfplumber` cannot extract text from a particular PDF, the alternatives below can be swapped in
by editing the extraction logic in the script:

- `pypdfium2` — good performance, handles some edge cases pdfplumber misses
- `pdfminer.six` — slower but very thorough text extraction
