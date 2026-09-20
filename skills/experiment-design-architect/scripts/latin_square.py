#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""latin_square.py — 拉丁方陣產生器(experiment-design-architect 附屬工具)

產生「標準拉丁方陣」與「Williams 平衡拉丁方陣」兩種對抗平衡序列，並把受試者
隨機（可重現）分派到各序列，輸出 CSV。方法說明與何時該用哪一種，見
`references/counterbalancing.md`；本腳本只管序列與分派表的產生，不做統計分析。

用法：
    python latin_square.py --conditions 4 --subjects 24 --seed 42
    python latin_square.py --conditions 4 --subjects 24 --seed 42 --method standard
    python latin_square.py --conditions 5 --subjects 20 --seed 1 --labels 低揭露,高揭露,對照,框架A,框架B
    python latin_square.py --conditions 4 --subjects 24 --seed 42 --out my_design

輸出（預設 --out ./output/latin_square_design，M4 修復：不直接寫 cwd；皆為 UTF-8 編碼 CSV）：
    <out>_standard_square.csv   標準拉丁方陣（列＝序列，欄＝呈現位置）
    <out>_williams_square.csv   Williams 平衡拉丁方陣（偶數 k 為 k 個序列；
                                 奇數 k 為 2k 個序列，見 references 說明）
    <out>_assignment.csv        受試者分派表：每位受試者對應哪個方法/序列，
                                 展開成每個呈現位置該做哪個條件

條件數 k 上限：本腳本未設硬上限，但 k 越大完全對抗平衡越不適用（見
references/counterbalancing.md 決策速查表），Williams 設計在 k 較大時仍可行。
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from random import Random

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def standard_latin_square(k: int) -> list[list[int]]:
    """標準拉丁方陣（cyclic method）：每列每欄每條件恰出現一次，1-indexed 條件編號。
    只控制位置效應，不保證相鄰配對（一階殘留）均衡——見 references/counterbalancing.md。
    """
    return [[((i + j) % k) + 1 for j in range(k)] for i in range(k)]


def _zigzag_base(k: int) -> list[int]:
    """Williams 設計的基底序列：1, k, 2, k-1, 3, k-2, ...（鋸齒排列）。"""
    base = []
    low, high = 1, k
    toggle = True
    for _ in range(k):
        if toggle:
            base.append(low)
            low += 1
        else:
            base.append(high)
            high -= 1
        toggle = not toggle
    return base


def _cyclic_rows(base: list[int], k: int) -> list[list[int]]:
    return [[((v - 1 + i) % k) + 1 for v in base] for i in range(k)]


def williams_latin_square(k: int) -> tuple[list[list[int]], bool]:
    """Williams 平衡拉丁方陣：每個「前導條件→後續條件」的有序配對(一階殘留效應)
    在整個設計中出現次數相等。

    偶數 k：k 個序列，每個有序配對恰出現 1 次。
    奇數 k：需要兩個方陣共 2k 個序列(基底方陣＋其鏡像方陣)，每個有序配對各出現 2 次
    ——這是文獻上奇數條件數的已知限制(無法只用 k 個序列達成一階殘留完全平衡)，
    不是本腳本的實作缺陷。

    回傳 (方陣列表, is_even)。
    """
    base = _zigzag_base(k)
    rows = _cyclic_rows(base, k)
    if k % 2 == 0:
        return rows, True
    mirror_rows = _cyclic_rows(list(reversed(base)), k)
    return rows + mirror_rows, False


def _verify_digram_balance(rows: list[list[int]], k: int) -> dict[tuple[int, int], int]:
    """驗證用：計算每個有序相鄰配對(a,b)在整個方陣中出現的次數。"""
    pairs: dict[tuple[int, int], int] = {}
    for row in rows:
        for a, b in zip(row, row[1:]):
            pairs[(a, b)] = pairs.get((a, b), 0) + 1
    return pairs


def write_square_csv(path: Path, rows: list[list[int]], labels: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sequence_id"] + [f"position_{j + 1}" for j in range(len(rows[0]))])
        for i, row in enumerate(rows, start=1):
            w.writerow([f"S{i}"] + [labels[c - 1] for c in row])


def assign_subjects(n_subjects: int, n_sequences: int, seed: int) -> list[int]:
    """把受試者輪流(round-robin，隨機起點與序列順序可重現)分派到序列編號(1-indexed)。"""
    rng = Random(seed)
    seq_order = list(range(1, n_sequences + 1))
    rng.shuffle(seq_order)
    return [seq_order[i % n_sequences] for i in range(n_subjects)]


def write_assignment_csv(
    path: Path,
    n_subjects: int,
    seed: int,
    standard_rows: list[list[int]],
    williams_rows: list[list[int]],
    labels: list[str],
) -> None:
    std_assign = assign_subjects(n_subjects, len(standard_rows), seed)
    wil_assign = assign_subjects(n_subjects, len(williams_rows), seed + 1)
    k = len(standard_rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = (
            ["subject_id", "standard_sequence_id"]
            + [f"standard_position_{j + 1}" for j in range(k)]
            + ["williams_sequence_id"]
            + [f"williams_position_{j + 1}" for j in range(k)]
        )
        w.writerow(header)
        for s in range(1, n_subjects + 1):
            std_seq = std_assign[s - 1]
            wil_seq = wil_assign[s - 1]
            std_row = standard_rows[std_seq - 1]
            wil_row = williams_rows[wil_seq - 1]
            w.writerow(
                [f"subj_{s:03d}", f"S{std_seq}"]
                + [labels[c - 1] for c in std_row]
                + [f"S{wil_seq}"]
                + [labels[c - 1] for c in wil_row]
            )


def main() -> int:
    ap = argparse.ArgumentParser(description="拉丁方陣產生與受試者分派(對抗平衡)")
    ap.add_argument("--conditions", type=int, required=True, help="條件數 k(至少 2)")
    ap.add_argument("--subjects", type=int, required=True, help="受試者總數 N")
    ap.add_argument("--seed", type=int, default=42, help="隨機種子(受試者→序列分派用，預設 42)")
    ap.add_argument(
        "--method",
        choices=["standard", "williams", "both"],
        default="both",
        help="輸出哪種方陣，預設兩種都出(方便比較)",
    )
    ap.add_argument(
        "--labels",
        default=None,
        help="條件名稱，逗號分隔，數量須等於 --conditions；不給則用 C1..Ck",
    )
    ap.add_argument("--out", default=None,
                     help="輸出檔名前綴(預設 ./output/latin_square_design，M4 修復：不直接寫 cwd)")
    args = ap.parse_args()

    if args.out is None:
        os.makedirs("output", exist_ok=True)
        args.out = os.path.join("output", "latin_square_design")
        print(f"[提醒] 未指定 --out，輸出預設寫到 {args.out}_*.csv", file=sys.stderr)

    k = args.conditions
    n = args.subjects
    if k < 2:
        sys.exit("[錯誤] --conditions 至少要 2")

    if args.labels:
        labels = [s.strip() for s in args.labels.split(",")]
        if len(labels) != k:
            sys.exit(f"[錯誤] --labels 提供 {len(labels)} 個名稱，與 --conditions {k} 不符")
    else:
        labels = [f"C{i}" for i in range(1, k + 1)]

    out_prefix = Path(args.out)

    standard_rows = standard_latin_square(k)
    williams_rows, is_even = williams_latin_square(k)

    # L5-a 修復(2026-09-20)：門檻改用實際序列數,不是 k——奇數 k 的 Williams
    # 設計有 2k 個序列(見 williams_latin_square 說明),用 k 判斷會低估序列數,
    # 對奇數條件數的實驗漏掉警告。依實際輸出的方法決定要看哪些序列數。
    seq_counts = []
    if args.method in ("standard", "both"):
        seq_counts.append(len(standard_rows))
    if args.method in ("williams", "both"):
        seq_counts.append(len(williams_rows))
    max_seq = max(seq_counts) if seq_counts else k
    if n < max_seq:
        print(f"[警告] 受試者數 {n} 小於序列數 {max_seq}，部分序列將分不到任何受試者，"
              f"建議 --subjects 至少為 {max_seq} 的倍數")

    # 產生時自我驗證一次，發現不平衡就中止而非默默輸出錯誤設計。
    std_pairs = _verify_digram_balance(standard_rows, k)
    wil_pairs = _verify_digram_balance(williams_rows, k)
    expected_pair_count = k * (k - 1)
    wil_counts = set(wil_pairs.values())
    if is_even:
        ok = len(wil_pairs) == expected_pair_count and wil_counts == {1}
    else:
        ok = len(wil_pairs) == expected_pair_count and wil_counts == {2}
    if not ok:
        sys.exit(
            "[錯誤] Williams 方陣一階殘留平衡驗證失敗，請回報此為程式錯誤"
            f"(涵蓋配對數={len(wil_pairs)}/{expected_pair_count}，次數分布={wil_counts})"
        )

    if args.method in ("standard", "both"):
        p = Path(f"{out_prefix}_standard_square.csv")
        write_square_csv(p, standard_rows, labels)
        print(f"[輸出] 標準拉丁方陣 → {p}({len(standard_rows)} 序列 × {k} 位置)")

    if args.method in ("williams", "both"):
        p = Path(f"{out_prefix}_williams_square.csv")
        write_square_csv(p, williams_rows, labels)
        parity = "偶數 k，一階殘留完全平衡(每配對恰1次)" if is_even else "奇數 k，需 2 個子方陣(每配對恰2次)"
        print(f"[輸出] Williams 平衡拉丁方陣 → {p}({len(williams_rows)} 序列 × {k} 位置；{parity})")

    assign_path = Path(f"{out_prefix}_assignment.csv")
    write_assignment_csv(assign_path, n, args.seed, standard_rows, williams_rows, labels)
    print(f"[輸出] 受試者分派表 → {assign_path}({n} 位受試者；seed={args.seed})")

    # L5-a 修復：_column_counts() 回傳的是「每欄相異條件數」(len(set(col)))，
    # 不是「出現次數」——舊標籤名實不符，容易被誤讀成每個條件出現幾次。
    print("\n[驗證] 標準方陣：每欄相異條件數 =", {v for v in _column_counts(standard_rows, k).values()})
    print("[驗證] Williams 方陣一階殘留配對次數分布 =", wil_counts, "(理論值：偶數k→{1}，奇數k→{2})")
    print("\n對抗平衡方法怎麼選、如何在分析中檢查序列效果，見 references/counterbalancing.md")
    return 0


def _column_counts(rows: list[list[int]], k: int) -> dict[int, int]:
    counts: dict[int, int] = {}
    for j in range(k):
        col = [row[j] for row in rows]
        counts[j] = len(set(col))  # 每欄應包含 k 個不同條件(標準方陣才成立，Williams奇數k不檢查)
    return counts


if __name__ == "__main__":
    sys.exit(main())
