#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""power_analysis.py — 先驗檢定力(a priori power)樣本數計算器
(survey-research-architect 附屬工具)

對應 SKILL.md Step 2「樣本數三算法取大者」的第 1 法：檢定力分析。本腳本用
statsmodels.stats.power 算三種最常見的商管問卷/量化研究情境，**SEM 不在本腳本
計算範圍內**(理由見下方 sem 子指令的輸出)——SEM 的檢定力邏輯建立在模型自由度、
RMSEA 虛無假設值上，用一般迴歸/相關/t 檢定的公式硬套會給錯誤的樣本數，寧可
明講改用專門工具，不是隨便算一個數字給你。

三個子指令：

1) 多元迴歸(Cohen's f²，R² 增量或整體模型):
   python power_analysis.py regression --predictors 3 --f2 0.15 --alpha 0.05 --power 0.80
   （--f2 也可用 --effect small/medium/large 對應 .02/.15/.35）

2) 相關係數(r):
   python power_analysis.py correlation --r 0.30 --alpha 0.05 --power 0.80
   （--r 也可用 --effect small/medium/large 對應 .10/.30/.50）

3) 兩組均值差(獨立樣本 t 檢定，Cohen's d):
   python power_analysis.py ttest --d 0.50 --alpha 0.05 --power 0.80 --ratio 1.0
   （--d 也可用 --effect small/medium/large 對應 .20/.50/.80；--ratio 為組2/組1人數比）

任一子指令加 `--n <實際可得樣本數>` 可反過來算「這個樣本數下的達成檢定力」，
不必再指定 --power。

4) SEM 提醒(不計算):
   python power_analysis.py sem

依賴：pip install statsmodels>=0.14（連帶安裝 scipy/numpy/pandas；FTestPowerF2 類別
      0.14 版才有，見下方 M7 修復說明）。
"""
from __future__ import annotations

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

EFFECT_PRESETS = {
    "f2": {"small": 0.02, "medium": 0.15, "large": 0.35},
    "r": {"small": 0.10, "medium": 0.30, "large": 0.50},
    "d": {"small": 0.20, "medium": 0.50, "large": 0.80},
}


def _require_statsmodels():
    try:
        import statsmodels.stats.power as smp  # noqa: F401
    except ImportError:
        sys.exit(
            "[錯誤] 缺少 statsmodels。請先安裝：pip install statsmodels\n"
            "（會連帶安裝 scipy/numpy/pandas，屬一次性環境設定，不影響腳本邏輯）"
        )
    if not hasattr(smp, "FTestPowerF2"):
        sys.exit(
            "[錯誤] 本機 statsmodels 版本過舊，沒有 FTestPowerF2 類別（0.14 版才引入）。\n"
            "         請升級：pip install --upgrade statsmodels"
        )
    _self_check_ftestpowerf2(smp)
    return smp


def _self_check_ftestpowerf2(smp) -> None:
    """M7 修復(2026-09-20)的啟動自檢:用 Cohen(1988)已知表值(u=3, f²=.15, α=.05,
    power=.80 → n≈76.7)驗證 FTestPowerF2 這次呼叫仍給出預期方向與量級的結果。
    statsmodels 官方文件自承 FTestPower 的 df_num/df_denom 語意「顛倒」，且未排除
    未來版本會把語意改正——若那天真的發生，FTestPowerF2 的參數命名若也跟著調整，
    本檢查會先炸掉，而不是讓改錯的 n 靜默流進論文(硬規則6:數字零容忍)。
    """
    ft = smp.FTestPowerF2()
    df_denom = ft.solve_power(effect_size=0.15, df_num=3, alpha=0.05, power=0.80)
    n = df_denom + 3 + 1
    if not (75 <= n <= 78):
        sys.exit(
            f"[錯誤] statsmodels 語意自檢失敗:u=3, f²=.15, α=.05, power=.80 應得 "
            f"n≈76.7(容許 75–78)，本機算出 n={n:.1f}。statsmodels 版本可能改了 "
            "FTestPowerF2 的參數語意，本腳本已停用以免算出的樣本數不可信——"
            "請回報此為程式錯誤，勿逕行採信下方結果。"
        )


def _resolve_effect(args, kind: str, flag_name: str) -> float:
    val = getattr(args, flag_name)
    if val is not None:
        return val
    if args.effect is not None:
        return EFFECT_PRESETS[kind][args.effect]
    sys.exit(f"[錯誤] 需提供 --{flag_name} 或 --effect small/medium/large 其中之一")


def cmd_regression(args) -> int:
    smp = _require_statsmodels()
    import numpy as np

    u = args.predictors
    if u < 1:
        sys.exit("[錯誤] --predictors 至少要 1")
    f2 = _resolve_effect(args, "f2", "f2")
    ft = smp.FTestPowerF2()

    print("# 多元迴歸先驗檢定力分析(Cohen's f²)")
    print(f"- 預測變項數(u) = {u}；效果量 f² = {f2}；alpha = {args.alpha}")
    print("- M7 修復(2026-09-20)：改用 statsmodels.stats.power.FTestPowerF2()，")
    print("  該類別直接吃 f²、df_num/df_denom 命名與教科書一致(舊版用 FTestPower()")
    print("  搭配官方文件自承『語意顛倒』的參數對應，一旦上游把語意改正會靜默算錯，")
    print("  已用 Cohen(1988)已知表值(u=3, f²=.15, α=.05, power=.80 → n≈76.7)驗證)。\n")

    if args.n is not None:
        n = args.n
        df_denom_resid = n - u - 1
        if df_denom_resid <= 0:
            sys.exit(f"[錯誤] n={n} 太小，殘差自由度 = n - u - 1 = {df_denom_resid} <= 0")
        power = ft.power(effect_size=f2, df_num=u, df_denom=df_denom_resid, alpha=args.alpha)
        print(f"[結果] 給定 n = {n}(殘差自由度 = {df_denom_resid}) → 達成檢定力 = {power:.4f}")
    else:
        df_denom_resid = ft.solve_power(effect_size=f2, df_num=u, alpha=args.alpha, power=args.power)
        n = df_denom_resid + u + 1
        print(f"[結果] 達到 power = {args.power} 所需最小樣本數 n ≈ {n:.1f}，建議取整數上界 n = {int(np.ceil(n))}")
    return 0


def cmd_correlation(args) -> int:
    smp = _require_statsmodels()
    import numpy as np

    r = _resolve_effect(args, "r", "r")
    if not (0 < abs(r) < 1):
        sys.exit("[錯誤] --r 須介於 0 與 1 之間(不含 0 與 1)")
    f2 = r ** 2 / (1 - r ** 2)
    ft = smp.FTestPowerF2()

    print("# 單一相關係數先驗檢定力分析")
    print(f"- 效果量 r = {r}；等效 Cohen's f² = r²/(1-r²) = {f2:.4f}；alpha = {args.alpha}")
    print("- 方法說明：單一相關係數的 t 檢定，數學上等價於「1 個預測變項的簡單迴歸」F 檢定")
    print("  （u=1），本腳本用此等價關係精算，而非傳統 Fisher z 常態近似表——因此算出的 n")
    print("  可能與 Cohen(1988)查表值有個位數差異(如 r=.30 本法得 n≈81 vs 傳統表約 84)，")
    print("  兩者皆為合理估計，屬方法差異而非錯誤，論文中請註明採用何種方法。")
    print("- M7 修復(2026-09-20)：改用 FTestPowerF2()，理由同 regression 子指令。\n")

    if args.n is not None:
        n = args.n
        resid_df = n - 1 - 1
        if resid_df <= 0:
            sys.exit(f"[錯誤] n={n} 太小")
        power = ft.power(effect_size=f2, df_num=1, df_denom=resid_df, alpha=args.alpha)
        print(f"[結果] 給定 n = {n} → 達成檢定力 = {power:.4f}")
    else:
        resid_df = ft.solve_power(effect_size=f2, df_num=1, alpha=args.alpha, power=args.power)
        n = resid_df + 1 + 1
        print(f"[結果] 達到 power = {args.power} 所需最小樣本數 n ≈ {n:.1f}，建議取整數上界 n = {int(np.ceil(n))}")
    return 0


def cmd_ttest(args) -> int:
    smp = _require_statsmodels()
    import numpy as np

    d = _resolve_effect(args, "d", "d")
    tt = smp.TTestIndPower()

    print("# 兩組獨立樣本均值差先驗檢定力分析(Cohen's d)")
    print(f"- 效果量 d = {d}；組2/組1人數比 ratio = {args.ratio}；alpha = {args.alpha}\n")

    if args.n is not None:
        power = tt.power(effect_size=d, nobs1=args.n, alpha=args.alpha, ratio=args.ratio)
        print(f"[結果] 給定組1 n = {args.n}(組2 n ≈ {args.n * args.ratio:.0f}) → 達成檢定力 = {power:.4f}")
    else:
        n1 = tt.solve_power(effect_size=d, alpha=args.alpha, power=args.power, ratio=args.ratio)
        n2 = n1 * args.ratio
        total = n1 + n2
        print(
            f"[結果] 達到 power = {args.power} 所需：組1 n ≈ {n1:.1f}、組2 n ≈ {n2:.1f}、"
            f"總樣本數 ≈ {total:.1f}(建議取整數上界)"
        )
    return 0


def cmd_sem(_args) -> int:
    print("# SEM(結構方程模型)先驗檢定力分析——本腳本不計算")
    print("""
原因：SEM 的檢定力邏輯與一般迴歸/相關/t 檢定不同源，不是同一組公式的延伸：
1. SEM 常見的檢定力分析是針對「模型整體適配度」而非單一係數，最普遍的作法是
   MacCallum, Browne & Sugawara (1996) 的 RMSEA 檢定力法：給定模型自由度(df)、
   虛無假設 RMSEA 與對立假設 RMSEA，反推所需樣本數——這需要先有完整的模型
   自由度(取決於觀察變項數、估計參數數)，不是套一個效果量數字就能算。
2. 若勉強借用 f²/r/d 的迴歸公式去估 SEM 樣本數，會忽略測量模型的因素負荷量、
   潛在變項數、模型複雜度對檢定力的影響，算出來的數字沒有理論依據，比不算還
   危險——會讓使用者誤以為有做過嚴謹的先驗檢定力分析。

請改用專門工具，不要用本腳本硬算：
- R 套件 semTools::findRMSEAsamplesize()（RMSEA 法，MacCallum et al. 1996）
- R 套件 pwrSEM 或 Wolf et al. (2013) 的模擬法(Monte Carlo power simulation)——
  蒙地卡羅法對含中介/調節的複雜模型更穩健，是目前頂刊審稿人較常引用的作法。
- 經驗法則(僅供初估、不能取代上述方法)：估計參數數 × 5–10 為最低樣本數下限
  (SKILL.md Step 2 已列此經驗法則作為三算法之一，本腳本的迴歸/相關/t檢定計算
  僅適用於問卷研究中「非 SEM 的單一假設檢定」部分，例如控制變項後的迴歸係數檢定)。
""")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="先驗檢定力樣本數計算器(survey-research-architect)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    common = dict(
        alpha={"type": float, "default": 0.05, "help": "顯著水準，預設 .05"},
        power={"type": float, "default": 0.80, "help": "目標檢定力，預設 .80"},
        n={"type": float, "default": None, "help": "若提供，改為計算此樣本數下的達成檢定力"},
        effect={"choices": ["small", "medium", "large"], "default": None, "help": "用 Cohen 慣例效果量代替明確數值"},
    )

    p_reg = sub.add_parser("regression", help="多元迴歸(Cohen's f²)")
    p_reg.add_argument("--predictors", type=int, required=True, help="迴歸式中的預測變項數(或 R² 增量的新增變項數)")
    p_reg.add_argument("--f2", type=float, default=None, help="Cohen's f² 效果量")
    for k, v in common.items():
        p_reg.add_argument(f"--{k}", **v)
    p_reg.set_defaults(func=cmd_regression)

    p_cor = sub.add_parser("correlation", help="單一相關係數(r)")
    p_cor.add_argument("--r", type=float, default=None, help="預期相關係數(絕對值)")
    for k, v in common.items():
        p_cor.add_argument(f"--{k}", **v)
    p_cor.set_defaults(func=cmd_correlation)

    p_tt = sub.add_parser("ttest", help="兩組獨立樣本均值差(Cohen's d)")
    p_tt.add_argument("--d", type=float, default=None, help="Cohen's d 效果量")
    p_tt.add_argument("--ratio", type=float, default=1.0, help="組2樣本數/組1樣本數比，預設 1.0(等組)")
    for k, v in common.items():
        p_tt.add_argument(f"--{k}", **v)
    p_tt.set_defaults(func=cmd_ttest)

    p_sem = sub.add_parser("sem", help="SEM 提醒(不計算，說明改用哪個工具)")
    p_sem.set_defaults(func=cmd_sem)

    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
