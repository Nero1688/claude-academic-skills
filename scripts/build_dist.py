#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_dist.py — 由 skills/ 重建 dist/ 的個別安裝包。

為什麼要有這支：dist/ 是手工維護時最容易漂移的地方。技能改了、新增了，
打包檔卻停在舊版——使用者下載到的是過期內容，而且不會有任何跡象。
2026-09-02 實測：repo 有 38 支技能，dist/ 只有 35 個 zip。

打包規格（Claude 技能上傳要求）：壓縮檔頂層是**單一技能資料夾**，
內含該技能的 SKILL.md。故路徑一律為 `<skill>/…`。

用法：
    python scripts/build_dist.py            # 重建全部
    python scripts/build_dist.py --check    # 只檢查是否同步，不寫檔（CI 用）
"""
import hashlib
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
DIST = os.path.join(ROOT, "dist")
CHECK = "--check" in sys.argv

SKIP_NAMES = {".DS_Store", "Thumbs.db"}
SKIP_DIRS = {"__pycache__", ".git"}


def files_of(skill):
    base = os.path.join(SKILLS, skill)
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn in SKIP_NAMES or fn.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, base).replace("\\", "/")
            out.append((full, f"{skill}/{rel}"))
    return sorted(out, key=lambda x: x[1])


def build(skill, path):
    # 固定時間戳，讓相同內容產生相同位元組——否則每次重建都變成一筆假 diff。
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for full, arc in files_of(skill):
            zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            with open(full, "rb") as f:
                z.writestr(zi, f.read())


# 文字檔一律把換行正規化再比對。
# Windows 上 git 會把工作區檔案轉成 CRLF、Linux runner 是 LF，若直接比 zip 位元組，
# 同樣的內容在兩個平台會算出不同雜湊——CI 因此把 38 支全部誤判為「內容過期」。
#
# 這裡列的是**二進位**副檔名，其餘一律視為文字。
# 用排除法而非白名單：白名單版漏掉了 .js、.html 與沒有副檔名的 LICENSE，
# 於是仍有三支誤判。本 repo 幾乎全是文字，漏列一種文字格式就會再踩一次；
# 反過來列二進位格式，新增文字類型時不必回頭改這裡。
BINARY_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
              ".skill", ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".mov",
              ".xlsx", ".docx", ".pptx", ".sav", ".dta", ".rdata")


def norm(arc, data):
    if arc.lower().endswith(BINARY_EXT):
        return data
    return data.replace(b"\r\n", b"\n")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def manifest_folder(skill):
    out = {}
    for full, arc in files_of(skill):
        with open(full, "rb") as f:
            out[arc] = sha(norm(arc, f.read()))
    return out


def manifest_zip(path):
    out = {}
    with zipfile.ZipFile(path) as z:
        for arc in z.namelist():
            out[arc] = sha(norm(arc, z.read(arc)))
    return out


skills = sorted(
    d for d in os.listdir(SKILLS)
    if os.path.isdir(os.path.join(SKILLS, d))
    and os.path.isfile(os.path.join(SKILLS, d, "SKILL.md"))
)
os.makedirs(DIST, exist_ok=True)
existing = {f[:-4] for f in os.listdir(DIST) if f.endswith(".zip")}

stale, missing, orphan = [], [], sorted(existing - set(skills))

for s in skills:
    target = os.path.join(DIST, f"{s}.zip")
    if not os.path.exists(target):
        missing.append(s)
        if not CHECK:
            build(s, target)
        continue
    try:
        same = manifest_zip(target) == manifest_folder(s)
    except Exception:
        same = False
    if not same:
        stale.append(s)
        if not CHECK:
            build(s, target)

if not CHECK:
    for o in orphan:
        os.remove(os.path.join(DIST, f"{o}.zip"))

print(f"技能 {len(skills)} 支 / dist {len(existing)} 個")
if missing:
    print(f"  缺少打包: {', '.join(missing)}")
if stale:
    print(f"  內容過期: {', '.join(stale)}")
if orphan:
    print(f"  多餘打包: {', '.join(orphan)}")

if CHECK:
    if missing or stale or orphan:
        print("\ndist/ 與 skills/ 不同步。請執行： python scripts/build_dist.py")
        sys.exit(1)
    print("  dist/ 與 skills/ 完全同步。")
else:
    print("  已重建完成。")
