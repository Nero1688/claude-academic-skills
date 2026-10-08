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
# 第二線索:系列除了顏色還要靠線型/標記分得出來(黑白印刷、色弱讀者)。
# Okabe-Ito 的黃(#E69F00)、淺藍(#56B4E9)、灰(#999999)在白底對比 <3:1,
# 第 5 條以後的系列只靠顏色幾乎看不見,線型與標記是唯一能分辨的線索。
LINESTYLES = ["-", (0, (5, 2)), (0, (1, 1.5)), (0, (5, 2, 1, 2)), (0, (8, 2)), (0, (3, 1, 1, 1, 1, 1)), (0, (1, 3))]
MARKERS = ["o", "s", "^", "D", "v", "P", "X"]
# 非顯著係數用的灰:#767676 在白底 4.54:1(原 #9a9a93 只有 2.83:1,細線幾乎看不見)
MUTED = "#767676"

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
        col = PALETTE[0] if sig else MUTED
        ax.plot([lo, hi], [yi, yi], color=col, lw=1.6, zorder=2)
        # 顯著=實心、不顯著=空心:不只靠顏色(灰階列印仍分得出來)
        ax.scatter([c], [yi], s=42, zorder=3, lw=1.4,
                   facecolors=col if sig else "white", edgecolors=col)
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
        ax.plot(x_grid, yv, color=PALETTE[i % len(PALETTE)], lw=2.2, label=lab,
                ls=LINESTYLES[i % len(LINESTYLES)])
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
        ax.plot(years, yv, color=PALETTE[i % len(PALETTE)], lw=2,
                ls=LINESTYLES[i % len(LINESTYLES)], marker=MARKERS[i % len(MARKERS)],
                ms=4.5, label=lab)
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


def _apply_pub_fonts(font="tw"):
    """car_plot 的字型設定。font="tw":英數 Times New Roman、中文標楷體(DFKai-SB),
    逐字形 fallback(matplotlib >= 3.6 支援 font.family 清單逐字形遞補);
    font="sans":沿用 set_style() 的無襯線(references/figure_style.md)。
    回傳 (實際字型清單, 缺漏字型清單);缺字型時誠實回報並警告,不假裝已套用。"""
    if font == "sans":
        return list(plt.rcParams["font.family"]), []
    from matplotlib import font_manager
    avail = {f.name for f in font_manager.fontManager.ttflist}
    wanted = ["Times New Roman", "DFKai-SB"]
    missing = [f for f in wanted if f not in avail]
    family = [f for f in wanted if f in avail]
    if "Times New Roman" in missing:
        family.insert(0, "DejaVu Serif")
    if "DFKai-SB" in missing:  # 標楷體的其他系統名稱,最後才退到正黑體
        family += [f for f in ("BiauKai", "Microsoft JhengHei") if f in avail][:1]
    family.append("DejaVu Sans")  # 最後防線:至少不出現方框
    plt.rcParams.update({"font.family": family, "axes.unicode_minus": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})  # 42=內嵌 TrueType,PDF 內文字可選取
    if missing:
        import warnings
        warnings.warn(f"本環境缺字型 {missing},已改用 {family};投稿前請於有字型的機器重出")
    return family, missing


def car_plot(rel_time, series, labels=None, ci=0.95, pct=True, event_day=0,
             highlight_window=None, lang="en", font="tw", xlabel=None, ylabel=None,
             note=None, ax=None):
    """短窗事件研究的平均累積異常報酬(CAAR)曲線:各組平均 CAR 路徑+信賴帶、事件日垂直線,可多組比較。
    與 event_study_plot 分工:那支畫交錯 DiD 的逐期係數;這支畫市場反應的累積報酬路徑。

    參數
    ----
    rel_time : 相對事件日的交易日(整數陣列,例 -10..10)。
    series   : 一組或多組(多組傳 list,例:家族 vs 非家族)。每組可為
               (a) 2D 陣列 n_events × len(rel_time):逐事件 CAR 路徑(例:事件研究輸出的長表
                   依 event_id × rel_day 樞紐成矩陣)。函式算平均與 t 型信賴區間,N 取自事件數;
               (b) dict(caar=..., ci_low=..., ci_high=..., n=...):已算好的平均與 CI
                   (例:事件研究輸出 es_caar_path.csv 的同名欄位)。照你給的 CI 畫,圖註會註明。
    labels   : 各組名稱;圖例自動附 (N = …)。
    ci       : 信賴水準(只用於 (a))。
    pct      : True → y 軸以 % 顯示(輸入為小數報酬)。
    event_day: 事件日 t = 0 的位置(垂直虛線)。
    highlight_window : 例 (-1, 1),以淡灰底標出主檢定窗。
    lang     : "en" 英文軸標與圖註(投稿)或 "zh" 中文(口試、中文期刊)。
    font     : "tw" → 英數 Times New Roman+中文標楷體;"sans" → 沿用 figure_style 的無襯線。
    note     : 選填,檢定結果字串(例 "CAR(−1, +1): BMP t = 3.10; Kolari–Pynnönen adjusted p = 0.004")。
               不給就不印任何檢定數字——函式不替你編。
    回傳 (fig, ax, info);info 含各組 N、事件日 CAAR、實際字型、缺漏字型、圖註字串。
    """
    set_style()
    fonts, missing = _apply_pub_fonts(font)
    zh = lang == "zh"
    rel_time = np.asarray(rel_time, float)
    if isinstance(series, dict) or (isinstance(series, np.ndarray) and series.ndim == 2):
        series = [series]
    if labels is None:
        labels = [(f"組別 {i + 1}" if zh else f"Group {i + 1}") for i in range(len(series))]
    labels = list(labels)
    if len(labels) != len(series):
        raise ValueError("labels 與 series 的組數不一致")
    scale = 100.0 if pct else 1.0
    line_styles = ["-", (0, (5, 2)), (0, (1, 1.5)), (0, (5, 2, 1, 2))]
    markers = ["o", "s", "^", "D"]

    if ax is None:
        fig, ax = plt.subplots(figsize=(6.4, 4.4))
    else:
        fig = ax.figure
    if highlight_window is not None:
        a, b = highlight_window
        ax.axvspan(a - 0.5, b + 0.5, color="#e6e6e3", alpha=0.6, lw=0, zorder=0)
    ax.axhline(0, color="#9a9a93", lw=1, ls=(0, (4, 3)), zorder=1)
    ax.axvline(event_day, color="#33332f", lw=1.0, ls=(0, (4, 3)), zorder=1)

    ns, at_event, sources = [], [], set()
    for i, (g, lab) in enumerate(zip(series, labels)):
        if isinstance(g, dict):
            mean = np.asarray(g["caar"], float)
            lo = np.asarray(g["ci_low"], float); hi = np.asarray(g["ci_high"], float)
            n = g.get("n")
            n = int(np.nanmax(np.asarray(n, float))) if n is not None else None
            sources.add("supplied")
        else:
            P = np.asarray(g, float)
            if P.ndim != 2 or P.shape[1] != len(rel_time):
                raise ValueError(f"第 {i + 1} 組 CAR 路徑矩陣須為 n_events × {len(rel_time)}")
            cnt = np.sum(np.isfinite(P), axis=0)
            if np.any(cnt < 2):
                raise ValueError("每個相對日至少需要 2 個事件才能算信賴區間")
            mean = np.nanmean(P, axis=0); sd = np.nanstd(P, axis=0, ddof=1)
            try:
                from scipy import stats as _st
                crit = _st.t.ppf(0.5 + ci / 2.0, cnt - 1)
                sources.add("t")
            except ImportError:  # 無 scipy 時退回常態臨界值,並在圖註明講
                crit = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(round(ci, 2), 1.96)
                sources.add("normal")
            half = crit * sd / np.sqrt(cnt)
            lo, hi = mean - half, mean + half
            n = int(cnt.max())
        if not (len(mean) == len(lo) == len(hi) == len(rel_time)):
            raise ValueError("caar / ci_low / ci_high 長度必須與 rel_time 一致")
        if np.any(lo > mean + 1e-12) or np.any(hi < mean - 1e-12):
            raise ValueError("CI 端點必須包住 CAAR(ci_low <= caar <= ci_high);請核對來源輸出")
        col = PALETTE[i % len(PALETTE)]
        ax.fill_between(rel_time, lo * scale, hi * scale, color=col, alpha=0.16, lw=0, zorder=2)
        ntxt = f" (N = {n:,})" if n is not None else ""
        ax.plot(rel_time, mean * scale, color=col, lw=2.0, ls=line_styles[i % 4],
                marker=markers[i % 4], ms=3.6, zorder=3, label=f"{lab}{ntxt}")
        ns.append(n)
        k = np.where(rel_time == event_day)[0]
        at_event.append(float(mean[k[0]]) if len(k) else None)

    ax.text(event_day, 0.98, (" 事件日" if zh else " Event day"), transform=ax.get_xaxis_transform(),
            ha="left", va="top", fontsize=8, color="#33332f")
    span = len(rel_time)
    step = 1 if span <= 12 else (2 if span <= 25 else 5)
    ticks = np.arange(np.ceil(rel_time.min() / step) * step, rel_time.max() + 1, step)
    ax.set_xticks(ticks); ax.set_xticklabels([f"{int(t)}" for t in ticks])
    ax.set_xlim(rel_time.min() - 0.5, rel_time.max() + 0.5)
    if xlabel is None:
        xlabel = "相對事件日（交易日）" if zh else "Trading days relative to the event date"
    if ylabel is None:
        unit = ("（%）" if zh else " (%)") if pct else ""
        ylabel = (f"平均累積異常報酬 CAAR{unit}" if zh else f"CAAR{unit}")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    _despine(ax); ax.legend(frameon=False, loc="best")

    # 圖註:信賴帶來源與累積起點自動印;檢定數字只印使用者給的 note
    start = int(rel_time.min())
    lines = []
    if zh:
        if "t" in sources:
            lines.append(f"陰影為平均 CAR 的 {ci:.0%} 信賴區間（橫斷面 t）；CAR 自第 {start} 日起累積。")
        if "normal" in sources:
            lines.append(f"陰影為平均 CAR 的 {ci:.0%} 信賴區間（常態近似，本環境無 scipy）；CAR 自第 {start} 日起累積。")
        if "supplied" in sources:
            lines.append("陰影為估計輸出提供的信賴區間。")
    else:
        if "t" in sources:
            lines.append(f"Shaded bands: {ci:.0%} confidence intervals of the mean CAR (cross-sectional t); "
                         f"CARs cumulate from day {start}.")
        if "normal" in sources:
            lines.append(f"Shaded bands: {ci:.0%} confidence intervals (normal approximation; scipy unavailable); "
                         f"CARs cumulate from day {start}.")
        if "supplied" in sources:
            lines.append("Shaded bands: confidence intervals as supplied by the estimation output.")
    if note:
        lines.append(str(note))
    note_txt = "\n".join(lines)
    fig.tight_layout(rect=(0, 0.03 + 0.035 * len(lines), 1, 1))
    fig.text(0.01, 0.01, note_txt, ha="left", va="bottom", fontsize=7.5, color="#33332f")
    return fig, ax, dict(n=ns, caar_at_event=at_event, fonts=fonts, fonts_missing=missing,
                         note=note_txt, ci_source=sorted(sources))
