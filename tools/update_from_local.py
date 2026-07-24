#!/usr/bin/env python3
"""update_from_local.py — 把你本機(Claude Code)最新版技能同步進本 repo,並自動套用合規處理。

用法(在 repo 根目錄執行):
    python tools/update_from_local.py --src "C:/Users/你的帳號/.claude/skills"
可選:
    --private "路徑/private_substitutions.txt"  去識別置換表(預設找 ../PRIVATE_do_not_upload/)
    --keep-local-compliant                      若你本機已自行維護合規版 SKILL.md,不覆蓋

處理內容:
  1. 複製 --src 下所有技能資料夾進 skills/(排除 EXCLUDED 清單內的技能,各有原因)
  2. 去除技能名中的機構前綴(*-phd-researcher -> phd-researcher)
  3. 換上 tools/compliant/ 的合規版 SKILL.md(ob-hrm-scale-adaptor、tej-data-scout)
  4. 剝除 tej-catalog.md 的 Part E(訂閱介面導航樹)並改寫檔頭
  5. 依私密置換表去識別化(檔案本身不含任何個資)
  6. 為 milestone/資格考/phd-researcher 加「範例模板」聲明
  7. orchestrator 一致性檢查:偵測指向「公開包不存在技能」的 dangling reference,
     並核對「可路由 N 個」是否等於實際技能數 −1;不一致則以 exit 1 中止,不讓壞包成形
完成後請務必再跑: bash scripts/sanitize_check.sh
"""
import argparse, os, re, shutil, pathlib, sys

# 不納入公開包的技能(每一項都要註明原因)
EXCLUDED = {
    "check-citations": "上游無授權,不可重製;README 已連結原 repo",
    "tw-opendata-scout": "使用者決定僅留私人庫(2026-07-24 v2.5.0)",
}


def check_dangling_refs(skills: pathlib.Path) -> int:
    """偵測 orchestrator 名錄裡指到『公開包不存在的技能』的 dangling reference。

    排除某支技能後,orchestrator 仍會沿用私人版內容而指向它——這種不一致
    在名錄型 skill 上很難用肉眼發現,故自動檢查。回傳問題數。
    """
    orch = skills / "research-orchestrator" / "SKILL.md"
    if not orch.exists():
        return 0
    text = orch.read_text(encoding="utf-8")
    present = {d.name for d in skills.iterdir() if d.is_dir()}
    dangling = sorted(n for n in EXCLUDED if n in text and n not in present)

    problems = 0
    if dangling:
        problems += len(dangling)
        print(f"[7][錯誤] orchestrator 指向公開包不存在的技能: {', '.join(dangling)}")
        print("        → 請改寫 skills/research-orchestrator/SKILL.md,移除該技能條目與路由行,")
        print("          並把『可路由 N 個』的數字改成公開包實際數字。")

    # 名錄宣稱的可路由數,應等於 skills 總數 − 1(orchestrator 不路由自己)
    expected = len(present) - 1
    for m in re.finditer(r"(?:可路由的|列出的)\s*(\d+)\s*個|家族（\s*(\d+)\s*個可路由成員", text):
        claimed = int(m.group(1) or m.group(2))
        if claimed != expected:
            problems += 1
            print(f"[7][錯誤] orchestrator 宣稱可路由 {claimed} 個,但公開包實際應為 {expected} 個")
            break
    if not problems:
        print(f"[7] orchestrator 一致性檢查通過(可路由 {expected} 個,無 dangling reference)")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--private", default=None)
    ap.add_argument("--keep-local-compliant", action="store_true")
    a = ap.parse_args()

    repo = pathlib.Path(__file__).resolve().parents[1]
    skills = repo / "skills"
    src = pathlib.Path(os.path.expanduser(a.src))
    if not src.is_dir():
        sys.exit(f"[錯誤] 找不到來源目錄: {src}")

    # 1) 複製(排除 check-citations)
    skills.mkdir(exist_ok=True)
    copied = 0
    for d in sorted(src.iterdir()):
        if not d.is_dir():
            continue
        if d.name in EXCLUDED:
            print(f"[skip] {d.name}({EXCLUDED[d.name]})")
            continue
        dst = skills / d.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(d, dst); copied += 1
    print(f"[1] 已同步 {copied} 支技能")

    # 2) 更名:去除技能名中的機構前綴(任何 *-phd-researcher -> phd-researcher)
    new = skills / "phd-researcher"
    for d in list(skills.iterdir()):
        if d.is_dir() and d.name.endswith("-phd-researcher") and d.name != "phd-researcher":
            if new.exists():
                shutil.rmtree(new)
            d.rename(new); print(f"[2] 已更名 {d.name} -> phd-researcher")

    # 3) 合規版 SKILL.md
    if not a.keep_local_compliant:
        for rel, comp in [("ob-hrm-scale-adaptor/SKILL.md", "ob-hrm-scale-adaptor.SKILL.md"),
                          ("tej-data-scout/SKILL.md", "tej-data-scout.SKILL.md")]:
            c = repo / "tools" / "compliant" / comp
            t = skills / rel
            if c.exists() and t.parent.exists():
                shutil.copyfile(c, t); print(f"[3] 已套用合規版: {rel}")
        print("    (若你本機版本有新增功能,請手動把新增內容合併進合規版,勿恢復舊的違規段落)")

    # 4) 剝除 Part E + 改寫檔頭
    cat = skills / "tej-data-scout/references/tej-catalog.md"
    if cat.exists():
        txt = cat.read_text(encoding="utf-8")
        i = txt.find("## Part E")
        if i != -1:
            txt = txt[:i].rstrip() + "\n"
        txt = "\n".join(l for l in txt.splitlines() if "Part E" not in l) + "\n"
        if "擷取自" in txt or "訂閱版" in txt.split("---")[0]:
            header = ("# 資料庫目錄(研究者自用快查表 · 以 TEJ 為範例)\n\n"
                      "> 本表整理自 TEJ 公開官網(https://www.tejwin.com/databank-solution/taiwan/),\n"
                      "> 僅供快速路由與初判;不含任何訂閱終端機的完整導航樹或欄位全表。\n"
                      "> 確切路徑與欄位以你自己合法訂閱的終端機、官方 tejdoc 文件、公開範例 CSV 為準。\n")
            parts = txt.split("\n---\n", 1)
            txt = header + "\n---\n" + (parts[1] if len(parts) == 2 else txt)
        cat.write_text(txt, encoding="utf-8"); print("[4] tej-catalog:已剝除 Part E / 檔頭合規")

    # 5) 去識別化(從私密檔讀置換表;本腳本不含任何個資)
    priv = pathlib.Path(a.private) if a.private else repo.parent / "PRIVATE_do_not_upload" / "private_substitutions.txt"
    subs = []
    if priv.exists():
        for line in priv.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=>" not in line:
                continue
            old_s, new_s = line.split("=>", 1)
            subs.append((old_s, new_s))
        changed = 0
        for p in skills.rglob("*"):
            if p.suffix.lower() not in (".md", ".txt", ".py", ".js", ".json"):
                continue
            try:
                t = p.read_text(encoding="utf-8")
            except Exception:
                continue
            o = t
            for x, y in subs:
                t = t.replace(x, y)
            if t != o:
                p.write_text(t, encoding="utf-8"); changed += 1
        print(f"[5] 去識別化:套用 {len(subs)} 條規則,改動 {changed} 檔")
    else:
        print(f"[5][警告] 找不到私密置換表({priv}),跳過去識別化 —— push 前務必先跑 sanitize_check!")

    # 6) 範例模板 banner
    BANNER = ("\n> ⚠️ **範例模板聲明**:以下修業規則/考科結構僅作為**結構範例**。"
              "各校規定不同,請以**你所屬系所最新公告**為準,並自行替換具體數字與考科。\n")
    for rel in ["phd-milestone-tracker/SKILL.md", "qual-exam-coach/SKILL.md", "phd-researcher/SKILL.md"]:
        p = skills / rel
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        if "範例模板聲明" in t:
            continue
        m = list(re.finditer(r"^---\s*$", t, flags=re.M))
        if len(m) >= 2:
            pos = m[1].end()
            t = t[:pos] + "\n" + BANNER + t[pos:]
            p.write_text(t, encoding="utf-8"); print(f"[6] 已加模板聲明: {rel}")

    # 7) orchestrator 一致性(dangling reference 偵測)
    problems = check_dangling_refs(skills)

    if problems:
        print("\n[未完成] 上列 orchestrator 不一致必須先修,否則公開包會指向不存在的技能。")
        print("         修好後再跑一次本工具,或手動確認後執行: bash scripts/sanitize_check.sh")
        sys.exit(1)
    print("\n[完成] 下一步請務必執行:  bash scripts/sanitize_check.sh")

if __name__ == "__main__":
    main()
