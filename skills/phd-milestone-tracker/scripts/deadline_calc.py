#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deadline_calc.py — 商管博士班關卡期限計算器(phd-milestone-tracker 附屬工具)

日期運算是決定論的,交給程式;skill 專心做解讀與風險判斷。

用法:
    python deadline_calc.py --enroll 112-09
    python deadline_calc.py --enroll 2023-09 --suspend-months 6 --today 115-01
    python deadline_calc.py --enroll 112-09 --qual-years 3 --max-years 7   # 規則覆寫
    # 已知事件日 → 反推申請窗口;並把所有期限匯出成行事曆檔(零連接器的提醒退路)
    python deadline_calc.py --enroll 112-09 --candidacy-date 115-05-20 --ics milestones.ics

年月一律支援民國(112-09)與西元(2023-09)兩種寫法;事件日支援 115-05-20 與 2026-05-20。

重要:內建規則值為《修業規則》基準值,**一律以系辦最新版簡章為準**;
若簡章數字不同,用 CLI 參數覆寫,不要改程式碼。

--ics 只是「寫出一個檔案」,不會讓任何行事曆自動出現提醒;要匯入後才算數。
(「沒真的設定就不說已設定」的紀律借鑑 anthropics/knowledge-work-plugins,Apache-2.0,
 small-business/shared/chain-seams.md;出處連結見 references/reminder-landing.md)
"""
import argparse
import calendar
import hashlib
import sys
from datetime import date, datetime, timedelta, timezone

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


def parse_ymd(s):
    """'115-05-20' / '2026-05-20' / '115/5/20' → date"""
    parts = s.replace("/", "-").strip().split("-")
    if len(parts) != 3:
        sys.exit(f"[錯誤] 日期需為 年-月-日:{s}")
    y, m, d = (int(x) for x in parts)
    if y < 1911:
        y += ROC_OFFSET
    try:
        return date(y, m, d)
    except ValueError:
        sys.exit(f"[錯誤] 日期不合法:{s}")


def minus_months(d, months):
    """日期往前推 N 個月;目標月沒有該日時取月底(如 3/31 往前一個月 → 2/28 或 2/29)。"""
    y, m = add_months(d.year, d.month, -months)
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def fmt_d(d):
    return f"民國 {d.year - ROC_OFFSET}/{d.month:02d}/{d.day:02d}(西元 {d:%Y-%m-%d})"


# ── iCalendar 匯出(RFC 5545;全天事件,避開時區把日期推前推後)──
def _ics_text(t):
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_fold(line):
    """每行 ≤75 位元組;續行以一個空白開頭。依字元切,不切斷 UTF-8 中文字。"""
    if len(line.encode("utf-8")) <= 75:
        return line
    chunks, cur = [], ""
    for ch in line:
        limit = 75 if not chunks else 74
        if len((cur + ch).encode("utf-8")) > limit:
            chunks.append(cur)
            cur = ch
        else:
            cur += ch
    chunks.append(cur)
    return "\r\n ".join(chunks)


def write_ics(path, events):
    """events: [{'summary', 'day': date, 'desc'}];回傳寫出的事件數。"""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//academic-claude-skills//phd-milestone-tracker//ZH-TW",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    for ev in events:
        uid = hashlib.sha1(f"{ev['summary']}|{ev['day'].isoformat()}".encode("utf-8")).hexdigest()[:16]
        lines += ["BEGIN:VEVENT", f"UID:{uid}@phd-milestone-tracker", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{ev['day']:%Y%m%d}",
                  f"DTEND;VALUE=DATE:{ev['day'] + timedelta(days=1):%Y%m%d}",
                  f"SUMMARY:{_ics_text(ev['summary'])}",
                  f"DESCRIPTION:{_ics_text(ev['desc'])}",
                  "TRANSP:TRANSPARENT",
                  # 前一天的提示;有些行事曆匯入時會忽略 VALARM,所以提前量另以獨立事件呈現
                  "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_ics_text(ev['summary'])}",
                  "TRIGGER:-P1D", "END:VALARM", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(_ics_fold(x) for x in lines) + "\r\n")
    return len(events)


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
    # ── 事件相對窗口:事件日已排定才算得出申請截止(基準值,以簡章為準)──
    ap.add_argument("--candidacy-date", default=None, help="博士候選人資格考核(前三章口試)日,如 115-05-20")
    ap.add_argument("--candidacy-lead-days", type=int, default=21, help="考核前幾天繳申請書(基準3週=21)")
    ap.add_argument("--seminar-date", default=None, help="博士生論文研討(公開發表)日")
    ap.add_argument("--seminar-lead-days", type=int, default=21, help="研討前幾天申請(基準3週=21)")
    ap.add_argument("--ppt-lead-days", type=int, default=3, help="研討前幾天交PPT(基準3天)")
    ap.add_argument("--defense-date", default=None, help="博士論文口試日")
    ap.add_argument("--defense-lead-months", type=int, default=1, help="口試前幾個月申請(基準1個月)")
    ap.add_argument("--ics", default=None, metavar="PATH",
                    help="把所有期限寫成行事曆檔(.ics);只寫檔,要自行匯入行事曆才會有提醒")
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

    # 事件日已排定 → 反推申請截止日(短窗口最容易漏,見 references/milestone-chain.md 第四節)
    today_d = date(today[0], today[1], 1) if args.today else date.today()
    ev_rows = []  # (名稱, 日期, 依據)
    if args.candidacy_date:
        cd = parse_ymd(args.candidacy_date)
        ev_rows += [("候選人資格考核申請書截止", cd - timedelta(days=args.candidacy_lead_days),
                     f"考核日 {cd:%Y-%m-%d} 前 {args.candidacy_lead_days} 天"),
                    ("博士候選人資格考核(前三章口試)", cd, "使用者提供的排定日")]
    if args.seminar_date:
        sd = parse_ymd(args.seminar_date)
        ev_rows += [("論文研討申請截止", sd - timedelta(days=args.seminar_lead_days),
                     f"發表日 {sd:%Y-%m-%d} 前 {args.seminar_lead_days} 天"),
                    ("論文研討 PPT 繳交截止", sd - timedelta(days=args.ppt_lead_days),
                     f"發表日 {sd:%Y-%m-%d} 前 {args.ppt_lead_days} 天"),
                    ("博士生論文研討(公開發表)", sd, "使用者提供的排定日")]
    if args.defense_date:
        dd = parse_ymd(args.defense_date)
        ev_rows += [("論文口試申請截止(須已通過著作審查)", minus_months(dd, args.defense_lead_months),
                     f"口試日 {dd:%Y-%m-%d} 前 {args.defense_lead_months} 個月"),
                    ("博士論文口試", dd, "使用者提供的排定日")]
    if ev_rows:
        ev_rows.sort(key=lambda r: r[1])
        print("\n## 依已排定事件反推的截止日")
        print("| 項目 | 日期 | 距今 | 換算依據 |")
        print("|---|---|---|---|")
        for name, d, rule in ev_rows:
            left = (d - today_d).days
            status = f"**已逾期 {-left} 天**" if left < 0 else (f"**剩 {left} 天 ⚠**" if left <= 14 else f"剩 {left} 天")
            print(f"| {name} | {fmt_d(d)} | {status} | {rule} |")
    print("\n## 發表分流門檻(依實際畢業年資,以簡章為準)")
    print("- 未滿 3 年:國科會學門前段(第一級)外文期刊 1 篇")
    print("- 3~5 年:SSCI / SCI(E) / TSSCI 1 篇")
    print("- 滿 5 年:EI / Scopus / EconLit 或國科會認可中文期刊 1 篇")
    print("\n※ 別忘了兩個非研究關卡:學術倫理課程、國際素養 6 點。")

    if args.ics:
        rule_note = "規則數字以系辦最新版簡章為準。"
        events = []
        for name, (y, m), rule in rows:
            day = date(y, m, 1)  # 月份精度:標在期限月 1 日,寧早勿晚
            desc = f"{rule}。月份精度,標在期限月 1 日(寧早勿晚);實際截止日以系辦公告為準。{rule_note}"
            is_redline = "紅線" in name
            events.append({"summary": f"{'【紅線】' if is_redline else '【期限】'}{name}", "day": day, "desc": desc})
            # 獨立的提前事件(不靠 VALARM,匯入後一定看得到);短窗口(指導教授申請)不適用
            for lead in ((180, 60) if is_redline else ()):
                events.append({"summary": f"【倒數 {lead} 天】{name}", "day": day - timedelta(days=lead),
                               "desc": f"距「{name}」(期限月 {y}-{m:02d})約 {lead} 天。{rule_note}"})
        for name, d, rule in ev_rows:
            events.append({"summary": f"【博班】{name}", "day": d, "desc": f"{rule}。{rule_note}"})
            if "截止" in name:
                events.append({"summary": f"【倒數 7 天】{name}", "day": d - timedelta(days=7),
                               "desc": f"距「{name}」7 天。{rule_note}"})
        n = write_ics(args.ics, events)
        print(f"\n## 行事曆檔\n- 已寫出 {n} 筆全天事件到 `{args.ics}`。")
        print("- **這只是檔案,還沒有進到任何行事曆**:匯入後才會出現;"
              "部分行事曆匯入時會忽略內建提醒,所以提前量另以「倒數 N 天」獨立事件呈現。")


if __name__ == "__main__":
    main()
