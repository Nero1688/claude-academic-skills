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


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


skills = sorted(
    d for d in os.listdir(SKILLS)
    if os.path.isdir(os.path.join(SKILLS, d))
    and os.path.isfile(os.path.join(SKILLS, d, "SKILL.md"))
)
os.makedirs(DIST, exist_ok=True)
existing = {f[:-4] for f in os.listdir(DIST) if f.endswith(".zip")}

stale, missing, orphan = [], [], sorted(existing - set(skills))
tmp = os.path.join(DIST, "_tmp.zip")

for s in skills:
    target = os.path.join(DIST, f"{s}.zip")
    if not os.path.exists(target):
        missing.append(s)
        if not CHECK:
            build(s, target)
        continue
    build(s, tmp)
    if digest(tmp) != digest(target):
        stale.append(s)
        if not CHECK:
            os.replace(tmp, target)
if os.path.exists(tmp):
    os.remove(tmp)

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
