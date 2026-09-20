"""
mgmt_figures.py — 管理／財務實證研究的出版級圖表工具
出版樣式底子改作自 nature-skills (nature-figure) by Yuan Yizhe, MIT License。
重新瞄準管理計量常用圖種。僅依賴 numpy + matplotlib;statsmodels 為選用(有則用於信賴帶)。
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Okabe-Ito 色盲友善調色盤
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#999999"]
BAND = "#9ec9e8"

def set_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.linewidth": 0.8, "axes.edgecolor": "#33332f",
        "xtick.major.width": 0.8, "ytick.major.width": 0.8,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "axes.labelsize": 11, "legend.fontsize": 9,
        "figure.dpi": 300, "savefig.dpi": 300,
    })

def _despine(ax):
    ax.spines[["top", "right"]].set_visible(False)

def save_fig(fig, name, outdir="."):
    """同時輸出 png(預覽)、pdf 與 svg(向量,投稿用),皆 300dpi。"""
    paths = []
    for ext in ("png", "pdf", "svg"):
        p = f"{outdir}/{name}.{ext}"
        fig.savefig(p, bbox_inches="tight")
        paths.append(p)
    return paths

def quadratic_turning_point_plot(x, y, xlabel="X", ylabel="Y",
                                 annotate=True, ax=None):
    """二次式倒U／U 轉折點圖:OLS 二次擬合 + 95% CI + 轉折點標示。
    回傳 (fig, ax, dict(b0,b1,b2,x_star,p_b2))。"""
    set_style()
    x = np.asarray(x, float); y = np.asarray(y, float)
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
    else:
        fig = ax.figure
    # 擬合
    try:
        import statsmodels.api as sm
        X = sm.add_constant(np.column_stack([x, x**2]))
        m = sm.OLS(y, X).fit()
        b0, b1, b2 = m.params; p_b2 = m.pvalues[2]
        gx = np.linspace(x.min(), x.max(), 200)
        G = sm.add_constant(np.column_stack([gx, gx**2]))
        sf = m.get_prediction(G).summary_frame(alpha=0.05)
        lo, hi, mean = sf["mean_ci_lower"], sf["mean_ci_upper"], sf["mean"]
    except Exception:
        b2c, b1c, b0c = np.polyfit(x, y, 2); b0, b1, b2 = b0c, b1c, b2c; p_b2 = np.nan
        gx = np.linspace(x.min(), x.max(), 200)
        mean = b0 + b1*gx + b2*gx**2
        resid = y - (b0 + b1*x + b2*x**2)
        se = resid.std(ddof=3); lo, hi = mean - 1.96*se, mean + 1.96*se
    x_star = -b1/(2*b2); y_star = b0 + b1*x_star + b2*x_star**2
    ax.scatter(x, y, s=14, color="#9a9a93", alpha=0.35, edgecolors="none", zorder=1)
    ax.fill_between(gx, lo, hi, color=BAND, alpha=0.55, lw=0, zorder=2, label="95% CI")
    ax.plot(gx, mean, color=PALETTE[0], lw=2.2, zorder=3, label="Fitted quadratic")
    if annotate:
        ax.axvline(x_star, ls=(0, (4, 3)), color=PALETTE[1], lw=1.3, zorder=2)
        ax.scatter([x_star], [y_star], s=46, color=PALETTE[1], zorder=5,
                   edgecolors="white", lw=1)
        ax.annotate(f"Turning point\n{xlabel}* = {x_star:.3f}",
                    xy=(x_star, y_star), xytext=(x_star + 0.06*(x.max()-x.min()), y_star),
                    fontsize=9, color="#33332f",
                    arrowprops=dict(arrowstyle="-", color=PALETTE[1], lw=0.8))
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    _despine(ax); ax.legend(frameon=False, loc="best")
    fig.tight_layout()
    return fig, ax, dict(b0=b0, b1=b1, b2=b2, x_star=x_star, p_b2=p_b2)

def coefficient_forest_plot(names, coefs, ci_low, ci_high, xlabel="Coefficient (95% CI)"):
    """係數森林圖:把迴歸係數與信賴區間橫向排列,虛線為 0。"""
    set_style()
    names = list(names); coefs = np.asarray(coefs, float)
    ci_low = np.asarray(ci_low, float); ci_high = np.asarray(ci_high, float)
    yloc = np.arange(len(names))[::-1]
    fig, ax = plt.subplots(figsize=(6.2, 0.5*len(names)+1.2))
    ax.axvline(0, color="#9a9a93", lw=1, ls=(0, (4, 3)), zorder=1)
    for yi, c, lo, hi in zip(yloc, coefs, ci_low, ci_high):
        sig = (lo > 0) or (hi < 0)
        col = PALETTE[0] if sig else "#9a9a93"
        ax.plot([lo, hi], [yi, yi], color=col, lw=1.6, zorder=2)
        ax.scatter([c], [yi], s=42, color=col, zorder=3, edgecolors="white", lw=1)
    ax.set_yticks(yloc); ax.set_yticklabels(names)
    ax.set_xlabel(xlabel); _despine(ax)
    fig.tight_layout()
    return fig, ax

def interaction_plot(x_grid, lines, xlabel="X", ylabel="Y", labels=None,
                     title_moderator="Moderator"):
    """交互作用／調節圖:在低/中/高調節值下各畫一條 X→Y 斜率線。
    lines: list of y arrays (與 x_grid 等長)。labels: 各線標籤。"""
    set_style()
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    labels = labels or [f"{title_moderator} {i}" for i in range(len(lines))]
    for i, (yv, lab) in enumerate(zip(lines, labels)):
        ax.plot(x_grid, yv, color=PALETTE[i % len(PALETTE)], lw=2.2, label=lab)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    _despine(ax); ax.legend(frameon=False, title=title_moderator)
    fig.tight_layout()
    return fig, ax

def group_comparison_plot(groups, means, errors=None, ylabel="Value", kind="bar"):
    """分組比較圖(例:家族 vs 非家族),bar 帶誤差線。"""
    set_style()
    x = np.arange(len(groups))
    fig, ax = plt.subplots(figsize=(0.9*len(groups)+2.5, 4.4))
    ax.bar(x, means, width=0.6, color=PALETTE[0], alpha=0.85,
           yerr=errors, capsize=4, error_kw=dict(lw=1, ecolor="#33332f"))
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylabel(ylabel); _despine(ax)
    fig.tight_layout()
    return fig, ax

def trend_plot(years, series, labels, ylabel="Value", xlabel="Year"):
    """時間趨勢圖:多組(如家族/非家族)逐年走勢。series: list of y arrays。"""
    set_style()
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for i, (yv, lab) in enumerate(zip(series, labels)):
        ax.plot(years, yv, color=PALETTE[i % len(PALETTE)], lw=2, marker="o",
                ms=4, label=lab)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    _despine(ax); ax.legend(frameon=False)
    fig.tight_layout()
    return fig, ax

def event_study_plot(rel_time, coef, ci_low, ci_high, ref_period=-1,
                     pre_joint_p=None, breakdown_M=None, onset=0,
                     xlabel="Periods relative to treatment",
                     ylabel="Coefficient (95% CI)", estimator=None,
                     pre_power_slope=None, ax=None):
    """事件研究圖(DiD 動態效果):逐期係數與 95% CI、參考期標記、處理時點垂直線、
    前期陰影,並在圖下方自動印出審稿人要看的兩個數字(前期聯合檢定 p、誠實區間 breakdown M̄)。

    參數
    ----
    rel_time  : 相對處理時點的期數(整數陣列,例 -4..4);參考期可以不在其中,函式會自動補 0。
    coef, ci_low, ci_high : 各期係數與 CI 端點(來自 did::aggte(type="dynamic")、
                fixest::sunab 或 iplot 的輸出;數字要能回溯到來源檔)。
    ref_period : 被省略(正規化為 0)的參考期,慣例為 -1;畫成空心點並標 "ref."。
    pre_joint_p: 前期係數聯合 Wald 檢定 p 值(did::aggte 的 Wpval 或 fixest::wald);
                None 表示未提供,圖註會印 "not reported"——不要編一個。
    breakdown_M: Rambachan & Roth (2023) 誠實區間的 breakdown 值 M̄*(HonestDiD 輸出);
                None 同上。
    onset      : 處理生效的相對期(預設 0);垂直線畫在 onset−0.5,前期陰影覆蓋其左側。
    estimator  : 估計量名稱字串(例 "Callaway & Sant'Anna (2021), not-yet-treated controls"),
                會印在圖註第一行——交錯採用時主圖的估計量名稱必須進圖。
    pre_power_slope : 選填,Roth (2022) 檢定力:設計以 80% 檢定力可偵測的線性前趨勢斜率。

    回傳 (fig, ax, info);info["note"] 是圖註字串,可直接貼進 caption。
    """
    set_style()
    rel_time = np.asarray(rel_time, int)
    coef = np.asarray(coef, float)
    ci_low = np.asarray(ci_low, float); ci_high = np.asarray(ci_high, float)
    if not (len(rel_time) == len(coef) == len(ci_low) == len(ci_high)):
        raise ValueError("rel_time / coef / ci_low / ci_high 長度必須一致")
    if np.any(ci_low > coef) or np.any(ci_high < coef):
        raise ValueError("CI 端點必須包住係數(ci_low <= coef <= ci_high);請核對來源輸出")
    # 參考期不在輸入中就補 0(它被正規化掉,不是估計值);在輸入中但非 0 則覆寫為 0 並提醒
    if ref_period not in rel_time:
        rel_time = np.append(rel_time, ref_period)
        coef = np.append(coef, 0.0); ci_low = np.append(ci_low, 0.0); ci_high = np.append(ci_high, 0.0)
    else:
        k = np.where(rel_time == ref_period)[0]
        if np.any(coef[k] != 0) or np.any(ci_low[k] != 0) or np.any(ci_high[k] != 0):
            import warnings
            warnings.warn(f"參考期 t={ref_period} 的係數/CI 非 0,已強制正規化為 0;"
                          "若你的估計量參考期不是這一期,請改 ref_period 參數")
            coef[k] = 0.0; ci_low[k] = 0.0; ci_high[k] = 0.0
    order = np.argsort(rel_time)
    rel_time, coef, ci_low, ci_high = rel_time[order], coef[order], ci_low[order], ci_high[order]
    is_ref = rel_time == ref_period

    if ax is None:
        fig, ax = plt.subplots(figsize=(6.4, 4.4))
    else:
        fig = ax.figure
    # 前期陰影與處理時點
    x_min, x_max = rel_time.min() - 0.5, rel_time.max() + 0.5
    ax.axvspan(x_min, onset - 0.5, color="#e6e6e3", alpha=0.6, lw=0, zorder=0)
    ax.axvline(onset - 0.5, color=PALETTE[1], lw=1.2, ls=(0, (4, 3)), zorder=1)
    ax.axhline(0, color="#9a9a93", lw=1, ls=(0, (4, 3)), zorder=1)
    # 係數與 CI(估計點實心;參考期空心且不畫 CI)
    est = ~is_ref
    ax.plot(rel_time, coef, color=PALETTE[0], lw=1.2, zorder=2)
    ax.errorbar(rel_time[est], coef[est],
                yerr=[coef[est] - ci_low[est], ci_high[est] - coef[est]],
                fmt="o", color=PALETTE[0], ecolor=PALETTE[0], elinewidth=1.4,
                capsize=3, ms=5, zorder=3, label="Estimate (95% CI)")
    ax.scatter(rel_time[is_ref], coef[is_ref], s=46, facecolors="white",
               edgecolors=PALETTE[0], lw=1.4, zorder=4, label=f"Reference period (t = {ref_period})")
    ax.annotate("ref.", xy=(ref_period, 0), xytext=(0, 9), textcoords="offset points",
                ha="center", fontsize=8, color="#33332f")
    ax.text(onset - 0.5, ax.get_ylim()[1], " treatment", ha="left", va="top",
            fontsize=8, color=PALETTE[1])
    ax.set_xticks(rel_time)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_xlim(x_min, x_max)
    _despine(ax); ax.legend(frameon=False, loc="best")

    # 圖註:審稿人要的數字自動印;沒給的印 not reported,不編數
    n_pre = int(np.sum((rel_time < onset) & est)); n_post = int(np.sum(rel_time >= onset))
    p_txt = f"{pre_joint_p:.3f}" if pre_joint_p is not None else "not reported"
    m_txt = f"{breakdown_M:.2f}" if breakdown_M is not None else "not reported"
    lines = []
    if estimator:
        lines.append(f"Estimator: {estimator}.")
    lines.append(f"Pre-period joint Wald p = {p_txt} ({n_pre} pre-period coefficients); "
                 f"robust to parallel-trends violations up to M̄ ≤ {m_txt} "
                 f"(Rambachan & Roth, 2023 breakdown value).")
    if pre_power_slope is not None:
        lines.append(f"Design detects a linear pre-trend of {pre_power_slope:g} with 80% power (Roth, 2022).")
    note = "\n".join(lines)
    fig.tight_layout(rect=(0, 0.06 + 0.035 * (len(lines) - 1), 1, 1))
    fig.text(0.01, 0.01, note, ha="left", va="bottom", fontsize=7.5, color="#33332f")
    return fig, ax, dict(note=note, ref_period=int(ref_period), n_pre=n_pre, n_post=n_post,
                         pre_joint_p=pre_joint_p, breakdown_M=breakdown_M)
