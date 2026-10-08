#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ci_checks.py — 技能包的結構一致性檢查（CI 用）。

每一項都對應一次**實際發生過**的問題，不是假想的：

  1. 內部標記殘留        不該發布的檔案標記仍留在包內
  2. 哨兵殘留            區塊哨兵沒被抽掉，代表 start/end 不成對
  3. NOTICE 覆蓋率       每支技能都要有授權登錄；global-opendata-scout 曾漏登四個月
  4. NOTICE 表格完整     空行會把 Markdown 表格截斷，後半段在 GitHub 上失去表頭
  5. README 技能數       badge 與實際數量不符（曾停在 35 而實際 38）
  6. description 長度    上傳時硬性上限 1024 字元，超過會被拒
  7. frontmatter 必填    name 與 description 缺一不可

用法：python scripts/ci_checks.py [repo根目錄]
結束碼 0 = 全通過；1 = 有問題（CI 會擋下）。
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SKILLS = os.path.join(ROOT, "skills")
DESC_MAX = 1024
# 不該發布的內部標記：清單放在 repo 外（環境變數 INTERNAL_MARKERS_FILE，每行一個字串），
# 免得清單本身寫進 repo。CI 上沒有這個檔就只檢查下方的未成對哨兵。
_mf = os.environ.get("INTERNAL_MARKERS_FILE", "")
INTERNAL_MARKERS = tuple(
    ln.strip() for ln in (open(_mf, encoding="utf-8").read().splitlines() if _mf and os.path.isfile(_mf) else [])
    if ln.strip() and not ln.startswith("#")
)
SENTINEL = "-".join(("PRIVATE", "ONLY"))  # 同步時應已被抽掉的區塊哨兵

problems = []


def err(msg):
    problems.append(msg)
    print(f"  [FAIL] {msg}")


def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


skill_dirs = sorted(
    d for d in os.listdir(SKILLS)
    if os.path.isdir(os.path.join(SKILLS, d))
    and os.path.isfile(os.path.join(SKILLS, d, "SKILL.md"))
)
print(f"技能數：{len(skill_dirs)}")

# ── 1 & 2：內部標記與哨兵殘留 ─────────────────────────────
print("\n[1] 內部標記殘留")
for dirpath, _, files in os.walk(SKILLS):
    for fn in files:
        if not fn.lower().endswith((".md", ".py", ".sh", ".json", ".txt")):
            continue
        p = os.path.join(dirpath, fn)
        t = read(p)
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        for m in INTERNAL_MARKERS:
            if m in t:
                err(f"{rel} 殘留內部標記「{m}」")
                break
        if SENTINEL in t:
            err(f"{rel} 殘留區塊哨兵（start/end 可能不成對）")
if not problems:
    print("  OK")

# ── 3 & 4：NOTICE ─────────────────────────────────────────
print("\n[3] NOTICE 授權登錄覆蓋率")
notice_path = os.path.join(ROOT, "NOTICE.md")
if not os.path.isfile(notice_path):
    err("找不到 NOTICE.md")
else:
    notice = read(notice_path)
    listed = {m.group(1) for m in re.finditer(r"^\|\s*([a-z][a-z0-9-]{4,})\s*\|", notice, re.M)}
    missing = sorted(set(skill_dirs) - listed)
    if missing:
        err("NOTICE.md 未登錄：" + ", ".join(missing))
    else:
        print(f"  OK（{len(skill_dirs)} 支全數登錄）")

    print("\n[4] NOTICE 表格未被空行截斷")
    lines = notice.split("\n")
    breaks = [
        i + 1 for i in range(1, len(lines) - 1)
        if lines[i].strip() == "" and lines[i - 1].startswith("|") and lines[i + 1].startswith("|")
    ]
    if breaks:
        err(f"NOTICE.md 第 {breaks} 行的空行會截斷表格，後半段將失去表頭")
    else:
        print("  OK")

# ── 5：README 技能數 ──────────────────────────────────────
print("\n[5] README 技能數一致")
readme_path = os.path.join(ROOT, "README.md")
if not os.path.isfile(readme_path):
    err("找不到 README.md")
else:
    readme = read(readme_path)
    m = re.search(r"badge/skills-(\d+)-", readme)
    if not m:
        err("README.md 找不到 skills badge")
    elif int(m.group(1)) != len(skill_dirs):
        err(f"README badge 寫 {m.group(1)} 支，實際 {len(skill_dirs)} 支")
    else:
        print(f"  OK（badge = {len(skill_dirs)}）")

# ── 6 & 7：frontmatter ───────────────────────────────────
print("\n[6] SKILL.md frontmatter")
for d in skill_dirs:
    p = os.path.join(SKILLS, d, "SKILL.md")
    t = read(p)
    if not t.startswith("---"):
        err(f"{d}/SKILL.md 沒有 frontmatter")
        continue
    fm = t.split("---", 2)[1]
    if not re.search(r"^name:", fm, re.M):
        err(f"{d}/SKILL.md frontmatter 缺 name")
    # description 三種合法寫法都要支援：雙引號、單引號、不加引號的裸量值。
    # （包內實際三種都有；只認雙引號會誤判成「缺 description」。）
    desc = None
    for pat in (r'^description:\s*"(.*?)"\s*$',
                r"^description:\s*'(.*?)'\s*$",
                r'^description:[ 	]*(\S.*?)\s*$'):
        m2 = re.search(pat, fm, re.S | re.M)
        if m2:
            desc = m2.group(1)
            break
    if desc is None:
        err(f"{d}/SKILL.md frontmatter 缺 description")
    elif len(desc) > DESC_MAX:
        err(f"{d}/SKILL.md description {len(desc)} 字元，超過上限 {DESC_MAX}")
print("  （逐支檢查完畢）")

# ── 8：dist 打包內不得含 PDF ──────────────────────────────
# 2026-09-02 實測：曾有打包檔內藏一份無授權聲明的第三方 PDF。
# 靠人工記得排除不可靠，所以在這裡自動擋。
# PDF 是最常見的「夾帶第三方著作」載體，故在打包層直接擋。
print("")
print("[8] dist 打包內無 PDF")
import zipfile
dist = os.path.join(ROOT, "dist")
if os.path.isdir(dist):
    found = []
    for fn in sorted(os.listdir(dist)):
        if not fn.endswith(".zip"):
            continue
        try:
            for n in zipfile.ZipFile(os.path.join(dist, fn)).namelist():
                if n.lower().endswith(".pdf"):
                    found.append(f"{fn} → {n}")
        except Exception as e:
            err(f"dist/{fn} 讀取失敗：{e}")
    if found:
        for f in found:
            err("打包內含 PDF（第三方著作風險）：" + f)
    else:
        print("  OK")
else:
    print("  （無 dist/，略過）")

print()
if problems:
    print(f"結果：{len(problems)} 項未通過。")
    sys.exit(1)
print("結果：全部通過。")
