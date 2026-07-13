#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deadline_calc.py — 商管博士班關卡期限計算器(phd-milestone-tracker 附屬工具)

日期運算是決定論的,交給程式;skill 專心做解讀與風險判斷。

用法:
    python deadline_calc.py --enroll 112-09
    python deadline_calc.py --enroll 2023-09 --suspend-months 6 --today 115-01
    python deadline_calc.py --enroll 112-09 --qual-years 3 --max-years 7   # 規則覆寫

年月一律支援民國(112-09)與西元(2023-09)兩種寫法。

重要:內建規則值為《修業規則》基準值,**一律以系辦最新版簡章為準**;
若簡章數字不同,用 CLI 參數覆寫,不要改程式碼。
"""
import argparse
import sys
from datetime import date

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROC_OFFSET = 1911


def parse_ym(s):
    """'112-09' / '2023-09' / '112/9' → (西元年, 月)"""
    s = s.replace("/", "-").strip()
    y, m = (int(x) for x in s.split("-"))
    if y < 1911:
        y += ROC_OFFSET
    if not 1 <= m <= 12:
        sys.exit(f"[錯誤] 月份不合法:{s}")
    return y, m


def add_months(y, m, months):
    t = (y * 12 + (m - 1)) + months
    return t // 12, t % 12 + 1


def fmt(y, m):
    return f"民國 {y - ROC_OFFSET}/{m:02d}(西元 {y}-{m:02d})"


def months_between(a, b):
    return (b[0] * 12 + b[1]) - (a[0] * 12 + a[1])


def main():
    ap = argparse.ArgumentParser(description="商管博士班關卡期限計算")
    ap.add_argument("--enroll", required=True, help="入學年月,如 112-09 或 2023-09")
    ap.add_argument("--suspend-months", type=int, default=0, help="累計休學月數(期限順延)")
    ap.add_argument("--today", default=None, help="以此年月當作今天(預設系統日期)")
    ap.add_argument("--qual-passed", default=None, help="資格考(主科+研方)全數通過年月;給了就算指導教授申請期限")
    # ── 規則參數(基準值,以簡章為準;不同就覆寫)──
    ap.add_argument("--qual-years", type=int, default=3, help="資格考退學紅線(入學滿N年,基準3)")
    ap.add_argument("--max-years", type=int, default=7, help="修業年限上限(基準7,不含休學)")
    ap.add_argument("--max-suspend-years", type=int, default=2, help="休學上限(基準2年)")
    ap.add_argument("--advisor-window-months", type=int, default=1, help="資格考通過後申請指導教授窗口(基準1個月)")
    args = ap.parse_args()

    ey, em = parse_ym(args.enroll)
    sus = args.suspend_months
    if sus > args.max_suspend_years * 12:
        print(f"[警告] 休學 {sus} 個月已超過基準上限 {args.max_suspend_years} 年,請即刻向系辦確認學籍狀態\n")
    today = parse_ym(args.today) if args.today else (date.today().year, date.today().month)

    # 換算慣例(與 skill 範例一致):「入學滿 N 年」的期限月 = 入學年月 + N 年 - 1 個月,
    # 意即該關卡須在下一學年開始前完成;休學月數往後順延。
    def redline(years):
        return add_months(ey, em, years * 12 + sus - 1)

    qual_dl = redline(args.qual_years)
    grad_dl = redline(args.max_years)

    rows = [
        ("學科資格考(退學紅線)", qual_dl,
         f"入學+{args.qual_years}年-1月{'+休學' + str(sus) + '月' if sus else ''};三年內未完成應予退學"),
        ("修業年限上限(畢業紅線)", grad_dl,
         f"入學+{args.max_years}年-1月{'+休學' + str(sus) + '月' if sus else ''};不含休學"),
    ]
    if args.qual_passed:
        qy, qm = parse_ym(args.qual_passed)
        adv = add_months(qy, qm, args.advisor_window_months)
        rows.insert(1, ("指導教授申請書(窗口)", adv,
                        f"資格考通過({fmt(qy, qm)})+{args.advisor_window_months}個月內"))

    print("# 關卡期限換算表")
    print(f"- 基準:入學 {fmt(ey, em)};休學 {sus} 個月;今天 {fmt(*today)}")
    print("- **所有規則數字以系辦最新版簡章為準**;不符時以簡章值用參數覆寫重算\n")
    print("| 關卡 | 最晚期限 | 距今 | 換算依據 |")
    print("|---|---|---|---|")
    for name, (y, m), rule in rows:
        left = months_between(today, (y, m))
        if left < 0:
            status = f"**已逾期 {-left} 個月**"
        elif left <= 6:
            status = f"**剩 {left} 個月 ⚠**"
        else:
            status = f"剩 {left} 個月(約 {left / 12:.1f} 年)"
        print(f"| {name} | {fmt(y, m)} | {status} | {rule} |")

    print("\n## 固定前置申請時間(事件相對,無法由入學日換算)")
    print("- 博士候選人資格考核(前三章口試):口試日前 **3 週** 繳申請書")
    print("- 博士生論文研討(公開發表):發表日前 **3 週** 申請、前 **3 天** 交 PPT")
    print("- 博士論文口試:口試日前 **1 個月** 申請,且須先通過學術著作審查")
    print("\n## 發表分流門檻(依實際畢業年資,以簡章為準)")
    print("- 未滿 3 年:國科會學門前段(第一級)外文期刊 1 篇")
    print("- 3~5 年:SSCI / SCI(E) / TSSCI 1 篇")
    print("- 滿 5 年:EI / Scopus / EconLit 或國科會認可中文期刊 1 篇")
    print("\n※ 別忘了兩個非研究關卡:學術倫理課程、國際素養 6 點。")


if __name__ == "__main__":
    main()
