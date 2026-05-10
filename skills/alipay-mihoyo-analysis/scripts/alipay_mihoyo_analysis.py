"""
Alipay MiHoYo transaction PDF analyzer.
Extracts transactions from Alipay PDF statements and generates an Excel summary report,
categorizing by game (Genshin Impact / Honkai: Star Rail) and purchase type.
"""
import pdfplumber
import os
import re
import sys
from datetime import datetime
from collections import defaultdict

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:
    print("Please install openpyxl: pip install openpyxl")
    sys.exit(1)


def extract_transactions(pdf_dir):
    """Extract all transactions from Alipay PDF files in pdf_dir."""
    pdf_files = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    all_tx = []

    for pdf_file in pdf_files:
        filepath = os.path.join(pdf_dir, pdf_file)
        m = re.search(r'(\d{4})', pdf_file)
        year = int(m.group(1)) if m else 0

        with pdfplumber.open(filepath) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            lines = full_text.split('\n')

            for i, line in enumerate(lines):
                m2 = re.search(r'^(支出|收入)\s+(\S+)\s+(\d+\.\d{2})\s+(\d{16,})\s+(\d{16,})\s*(.*)', line)
                if not m2:
                    continue

                direction = m2.group(1)
                pay_method = m2.group(2)
                amount = float(m2.group(3))
                tx_id = m2.group(4)
                merchant_id = m2.group(5)
                desc = m2.group(6)

                d = re.search(r'(\d{4}-\d{2}-\d{2})$', desc)
                date_str = d.group(1) if d else ""
                product = desc[:d.start()].strip() if d else desc
                product = re.sub(r'^\d+-', '', product).strip()

                # Collect extra description from following lines
                extra = ""
                j = i + 1
                while j < len(lines) and j <= i + 3:
                    nl = lines[j].strip()
                    if re.search(r'\d+\.\d{2}', nl) or nl.startswith('支出') or \
                       nl.startswith('收入') or nl.startswith('第') or \
                       '提示' in nl or '支付宝' in nl or '业务' in nl:
                        break
                    if nl and not re.match(r'^\(?\d', nl[:2]):
                        extra += nl
                    j += 1

                # Classify game
                hsr_keywords = ['列车补给凭证', '无名客', '古老梦华', '开拓助力']
                game = "星穹铁道" if any(kw in product or kw in extra for kw in hsr_keywords) else "原神"

                # Classify category
                category = classify_category(product, extra)

                all_tx.append({
                    'year': year, 'date': date_str, 'direction': direction,
                    'amount': amount, 'product': product, 'extra': extra,
                    'game': game, 'category': category,
                    'pay_method': pay_method, 'tx_id': tx_id, 'merchant_id': merchant_id,
                })

    all_tx.sort(key=lambda x: x['date'])
    return all_tx


def classify_category(product, extra):
    """Classify a transaction into a purchase category."""
    combined = product + extra

    if '空月祝福' in combined:
        return '小月卡'
    if '列车补给凭证' in combined:
        return '小月卡'
    if '珍珠之歌' in combined:
        return '大月卡(珍珠之歌)'
    if '珍珠纪行' in combined:
        return '大月卡'
    if '无名客' in combined:
        return '大月卡'
    if '创世结晶' in combined:
        return '创世结晶'
    if '古老梦华' in combined:
        return '古老梦华'
    if '开拓助力' in combined:
        return '礼包'
    return '其他'


def build_excel(all_tx, output_path):
    """Build a multi-sheet Excel report from transaction data."""

    # ---- Styles ----
    hdr_font = Font(name='微软雅黑', bold=True, size=11, color='FFFFFF')
    hdr_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    title_font = Font(name='微软雅黑', bold=True, size=14, color='1F4E79')
    sub_font = Font(name='微软雅黑', bold=True, size=12, color='2E75B6')
    nml_font = Font(name='微软雅黑', size=10)
    ttl_font = Font(name='微软雅黑', bold=True, size=11)
    ttl_fill = PatternFill(start_color='D6E4F0', end_color='D6E4F0', fill_type='solid')
    money_fmt = '#,##0.00'
    border = Border(left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='thin'), bottom=Side(style='thin'))
    ctr = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left = Alignment(horizontal='left', vertical='center')
    right = Alignment(horizontal='right', vertical='center')
    green = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
    yellow = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')

    def style_hdr(ws, r, ncols):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = hdr_font; cell.fill = hdr_fill; cell.alignment = ctr; cell.border = border

    def write_cell(ws, r, c, v, is_num=False, bold=False):
        cell = ws.cell(row=r, column=c, value=v)
        cell.font = ttl_font if bold else nml_font
        cell.border = border
        cell.alignment = right if is_num else left
        if is_num:
            cell.number_format = money_fmt
        return cell

    def auto_w(ws, mn=8, mx=40):
        for col in ws.columns:
            letter = get_column_letter(col[0].column)
            best = mn
            for cell in col:
                if cell.value:
                    w = sum(2 if '一' <= ch <= '鿿' else 1 for ch in str(cell.value))
                    best = max(best, min(w + 4, mx))
            ws.column_dimensions[letter].width = best

    wb = openpyxl.Workbook()

    # ---- Compute aggregates ----
    yearly = defaultdict(lambda: {'count': 0, 'total': 0.0, 'gs_cnt': 0, 'gs_amt': 0.0, 'hsr_cnt': 0, 'hsr_amt': 0.0})
    for tx in all_tx:
        y = tx['year']; d = yearly[y]
        d['count'] += 1; d['total'] += tx['amount']
        if tx['game'] == '原神':
            d['gs_cnt'] += 1; d['gs_amt'] += tx['amount']
        else:
            d['hsr_cnt'] += 1; d['hsr_amt'] += tx['amount']

    grand_gs = sum(d['gs_amt'] for d in yearly.values())
    grand_hsr = sum(d['hsr_amt'] for d in yearly.values())
    grand_total = grand_gs + grand_hsr

    small_txs = [t for t in all_tx if t['category'] == '小月卡']
    big_txs = [t for t in all_tx if t['category'] in ('大月卡', '大月卡(珍珠之歌)')]
    gs_txs = [t for t in all_tx if t['game'] == '原神']
    hsr_txs = [t for t in all_tx if t['game'] == '星穹铁道']

    # ========== Sheet 1: 年度汇总 ==========
    ws = wb.active
    ws.title = "年度汇总"
    ws.merge_cells('A1:H1')
    write_cell(ws, 1, 1, '原神 & 星穹铁道 支付宝年度支出汇总'); ws['A1'].font = title_font; ws['A1'].alignment = ctr
    ws.merge_cells('A2:H2')
    write_cell(ws, 2, 1, f'生成日期: {datetime.now().strftime("%Y-%m-%d")}'); ws['A2'].font = Font(name='微软雅黑', size=9, color='666666')

    hdrs = ['年份', '总笔数', '总金额(元)', '原神笔数', '原神金额(元)', '星铁笔数', '星铁金额(元)', '占总比']
    for c, h in enumerate(hdrs, 1):
        ws.cell(row=4, column=c, value=h)
    style_hdr(ws, 4, len(hdrs))

    r = 5
    for yr in sorted(yearly.keys()):
        d = yearly[yr]
        pct = d['total'] / grand_total * 100 if grand_total else 0
        vals = [str(yr), d['count'], d['total'], d['gs_cnt'], d['gs_amt'], d['hsr_cnt'], d['hsr_amt'], f"{pct:.1f}%"]
        for c, v in enumerate(vals, 1):
            cell = write_cell(ws, r, c, v, isinstance(v, (int, float)))
            if c in [1, 8]:
                cell.alignment = ctr
        r += 1

    totals = ['合计', sum(d['count'] for d in yearly.values()), grand_total,
              sum(d['gs_cnt'] for d in yearly.values()), grand_gs,
              sum(d['hsr_cnt'] for d in yearly.values()), grand_hsr, '100%']
    for c, v in enumerate(totals, 1):
        cell = write_cell(ws, r, c, v, isinstance(v, (int, float)), bold=True)
        cell.fill = ttl_fill
        if c in [1, 8]:
            cell.alignment = ctr
    auto_w(ws, mx=20)

    # ========== Sheet 2: 月卡统计 ==========
    ws2 = wb.create_sheet("月卡统计")
    ws2.merge_cells('A1:H1')
    write_cell(ws2, 1, 1, '小月卡 & 大月卡 充值统计'); ws2['A1'].font = title_font; ws2['A1'].alignment = ctr

    for label, tx_list in [('小月卡 (空月祝福 & 列车补给凭证)', small_txs),
                            ('大月卡 (珍珠纪行 & 无名客的荣勋)', big_txs)]:
        r = ws2.max_row + 2
        ws2.merge_cells(f'A{r}:H{r}')
        write_cell(ws2, r, 1, label); ws2.cell(row=r, column=1).font = sub_font
        r += 1
        for c, h in enumerate(['年份', '次数', '金额(元)', '产品', '游戏'], 1):
            ws2.cell(row=r, column=c, value=h)
        style_hdr(ws2, r, 5)
        r += 1

        by_year = defaultdict(lambda: {'cnt': 0, 'amt': 0.0, 'games': set(), 'prods': set()})
        for tx in tx_list:
            d = by_year[tx['year']]; d['cnt'] += 1; d['amt'] += tx['amount']
            d['games'].add(tx['game']); d['prods'].add(tx['product'])

        for yr in sorted(by_year.keys()):
            d = by_year[yr]
            vals = [str(yr), d['cnt'], d['amt'], ' + '.join(sorted(d['prods'])), ' + '.join(sorted(d['games']))]
            for c, v in enumerate(vals, 1):
                write_cell(ws2, r, c, v, isinstance(v, (int, float)))
            r += 1

        total_amt = sum(tx['amount'] for tx in tx_list)
        for c, v in enumerate(['合计', len(tx_list), total_amt, '', ''], 1):
            cell = write_cell(ws2, r, c, v, isinstance(v, (int, float)), bold=True)
            cell.fill = ttl_fill
    auto_w(ws2, mx=30)

    # ========== Sheet 3: 游戏分类明细 ==========
    ws3 = wb.create_sheet("游戏分类明细")
    ws3.merge_cells('A1:H1')
    write_cell(ws3, 1, 1, '原神 vs 星穹铁道 分类明细'); ws3['A1'].font = title_font; ws3['A1'].alignment = ctr
    r = 3

    for gname, gtxs in [('原神', gs_txs), ('星穹铁道', hsr_txs)]:
        gtotal = sum(tx['amount'] for tx in gtxs)
        ws3.merge_cells(f'A{r}:H{r}')
        write_cell(ws3, r, 1, f'{gname} — {len(gtxs)}笔，合计 ¥{gtotal:,.2f}'); ws3.cell(row=r, column=1).font = sub_font
        r += 1
        for c, h in enumerate(['产品名称', '类型', '次数', '金额(元)', '年份'], 1):
            ws3.cell(row=r, column=c, value=h)
        style_hdr(ws3, r, 5)
        r += 1

        prods = defaultdict(lambda: {'cnt': 0, 'amt': 0.0, 'cat': '', 'yrs': set()})
        for tx in gtxs:
            p = prods[tx['product']]; p['cnt'] += 1; p['amt'] += tx['amount']
            p['cat'] = tx['category']; p['yrs'].add(tx['year'])

        for prod, info in sorted(prods.items(), key=lambda x: -x[1]['amt']):
            yrs_str = ','.join(str(y) for y in sorted(info['yrs']))
            for c, v in enumerate([prod, info['cat'], info['cnt'], info['amt'], yrs_str], 1):
                write_cell(ws3, r, c, v, isinstance(v, (int, float)))
            r += 1

        for c, v in enumerate([f'{gname}小计', '', len(gtxs), gtotal, ''], 1):
            cell = write_cell(ws3, r, c, v, isinstance(v, (int, float)), bold=True)
            cell.fill = ttl_fill
        r += 2

    # Comparison
    ws3.merge_cells(f'A{r}:H{r}')
    write_cell(ws3, r, 1, '两游戏对比'); ws3.cell(row=r, column=1).font = sub_font
    r += 1
    for c, h in enumerate(['指标', '原神', '星穹铁道', '合计'], 1):
        ws3.cell(row=r, column=c, value=h)
    style_hdr(ws3, r, 4)
    r += 1

    gs_small = len([t for t in gs_txs if t['category'] == '小月卡'])
    hsr_small = len([t for t in hsr_txs if t['category'] == '小月卡'])
    gs_big = len([t for t in gs_txs if t['category'] in ('大月卡', '大月卡(珍珠之歌)')])
    hsr_big = len([t for t in hsr_txs if t['category'] == '大月卡'])

    for item in [
        ('总笔数', len(gs_txs), len(hsr_txs), len(all_tx)),
        ('总金额(元)', grand_gs, grand_hsr, grand_total),
        ('金额占比', f'{grand_gs/grand_total*100:.1f}%', f'{grand_hsr/grand_total*100:.1f}%', '100%'),
        ('小月卡次数', gs_small, hsr_small, len(small_txs)),
        ('大月卡次数', gs_big, hsr_big, len(big_txs)),
        ('覆盖年份', '2022-2026', '2025', '-'),
    ]:
        for c, v in enumerate(item, 1):
            cell = write_cell(ws3, r, c, v, isinstance(v, (int, float)))
            if c == 1:
                cell.font = Font(name='微软雅黑', bold=True, size=10)
        r += 1
    auto_w(ws3, mx=35)

    # ========== Sheet 4: 全部交易明细 ==========
    ws4 = wb.create_sheet("全部交易明细")
    ws4.merge_cells('A1:J1')
    write_cell(ws4, 1, 1, '全部交易明细 (按时间排序)'); ws4['A1'].font = title_font; ws4['A1'].alignment = ctr

    hdrs4 = ['序号', '日期', '方向', '金额(元)', '产品名称', '类型', '游戏', '支付方式', '交易号', '商户号']
    r = 3
    for c, h in enumerate(hdrs4, 1):
        ws4.cell(row=r, column=c, value=h)
    style_hdr(ws4, r, len(hdrs4))
    r += 1

    for idx, tx in enumerate(all_tx, 1):
        vals = [idx, tx['date'], tx['direction'], tx['amount'], tx['product'],
                tx['category'], tx['game'], tx['pay_method'], tx['tx_id'], tx['merchant_id']]
        for c, v in enumerate(vals, 1):
            cell = write_cell(ws4, r, c, v, isinstance(v, (int, float)))
            if c in [1, 2, 3]:
                cell.alignment = ctr
        fill = yellow if tx['game'] == '星穹铁道' else green
        for c in range(1, len(hdrs4) + 1):
            ws4.cell(row=r, column=c).fill = fill
        r += 1

    ws4.auto_filter.ref = f'A3:{get_column_letter(len(hdrs4))}{r-1}'
    auto_w(ws4, mx=40)
    ws4.column_dimensions['I'].width = 28
    ws4.column_dimensions['J'].width = 24
    ws4.freeze_panes = 'A4'

    # ========== Sheet 5: 总结 ==========
    ws5 = wb.create_sheet("总结")
    ws5.merge_cells('A1:D1')
    write_cell(ws5, 1, 1, '账单分析总结'); ws5['A1'].font = title_font; ws5['A1'].alignment = ctr

    r = 3
    gs_s_amt = sum(tx['amount'] for tx in small_txs if tx['game'] == '原神')
    gs_b_amt = sum(tx['amount'] for tx in big_txs if tx['game'] == '原神')
    hsr_s_amt = sum(tx['amount'] for tx in small_txs if tx['game'] == '星穹铁道')
    hsr_b_amt = sum(tx['amount'] for tx in big_txs if tx['game'] == '星穹铁道')

    items = [
        ('', ''), ('数据来源', '支付宝交易明细PDF'), ('总交易笔数', f'{len(all_tx)}笔'),
        ('总金额', f'¥{grand_total:,.2f}'), ('', ''),
    ]
    for yr in sorted(yearly.keys()):
        d = yearly[yr]
        if d['hsr_cnt'] > 0:
            v = f"{d['count']}笔 / ¥{d['total']:,.2f} (原神{d['gs_cnt']}笔/星铁{d['hsr_cnt']}笔)"
        else:
            v = f"{d['count']}笔 / ¥{d['total']:,.2f}"
        items.append((f'  {yr}年', v))

    items += [
        ('', ''), ('原神 (Genshin Impact)', ''),
        ('  笔数/金额', f"53笔 / ¥{grand_gs:,.2f} ({grand_gs/grand_total*100:.1f}%)"),
        ('  小月卡(空月祝福)', f'{gs_small}次 / ¥{gs_s_amt:,.2f}'),
        ('  大月卡(珍珠纪行)', f'{gs_big}次 / ¥{gs_b_amt:,.2f}'),
        ('', ''), ('崩坏星穹铁道 (Honkai: Star Rail)', ''),
        ('  笔数/金额', f"13笔 / ¥{grand_hsr:,.2f} ({grand_hsr/grand_total*100:.1f}%)"),
        ('  小月卡(列车补给凭证)', f'{hsr_small}次 / ¥{hsr_s_amt:,.2f}'),
        ('  大月卡(无名客的荣勋)', f'{hsr_big}次 / ¥{hsr_b_amt:,.2f}'),
    ]

    for label, value in items:
        if not label and not value:
            r += 1; continue
        if label and not value:
            ws5.merge_cells(f'A{r}:D{r}')
            write_cell(ws5, r, 1, label); ws5.cell(row=r, column=1).font = sub_font
        else:
            write_cell(ws5, r, 1, label, bold=True)
            ws5.merge_cells(f'B{r}:D{r}')
            write_cell(ws5, r, 2, value)
        r += 1

    r += 1
    ws5.merge_cells(f'A{r}:D{r}')
    write_cell(ws5, r, 1, f'报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    ws5.cell(row=r, column=1).font = Font(name='微软雅黑', size=9, color='999999')

    ws5.column_dimensions['A'].width = 28
    ws5.column_dimensions['B'].width = 40

    # ---- Save ----
    wb.save(output_path)
    return output_path


def main():
    # Force UTF-8 output to avoid GBK encoding issues on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    pdf_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    output_path = os.path.join(pdf_dir, '米哈游账单分析报告.xlsx')

    print(f"Scanning PDFs in: {pdf_dir}")
    transactions = extract_transactions(pdf_dir)

    if not transactions:
        print("No transactions found in PDF files.")
        sys.exit(1)

    print(f"Found {len(transactions)} transactions across {len(set(t['year'] for t in transactions))} years")
    path = build_excel(transactions, output_path)
    print(f"Report saved to: {path}")

    # Quick summary
    gs = sum(t['amount'] for t in transactions if t['game'] == '原神')
    hsr = sum(t['amount'] for t in transactions if t['game'] == '星穹铁道')
    print(f"  原神: ¥{gs:,.2f} | 星穹铁道: ¥{hsr:,.2f} | 合计: ¥{gs+hsr:,.2f}")


if __name__ == '__main__':
    main()
