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
