# 穩健性矩陣：依識別策略列出審稿人會要的每一項（含 R 函式）

本檔延伸 SKILL.md Step 4「診斷與安慰劑矩陣」與 Step 5「審稿人攻防表」。
與 `references/estimator-playbook.md` 的分工：那裡是**主估計**的語法；這裡是主估計
跑完之後，頂刊審稿人會逐項要的**穩健性與敏感度**，每項附「審稿人會怎麼問」與
R 套件／函式名，讓你在被問之前就把表做好。套件以 CRAN 現行版為準，函式名以
`?函式` 為準；部分前緣套件（如 `HonestDiD`、`pretrends`、`augsynth`）可能只在作者
GitHub 發布或曾自 CRAN 下架，安裝前確認來源；估計量與套件版本一律寫進再現性聲明
（SKILL.md 紅線 4）。

三個等級：**必做**＝沒有就是 Major（財務家族常是 Fatal）；**加分**＝有則攻防表多一列；
**情境觸發**＝符合條件才做。四軸對應見 `q1-journal-reviewer` 的
`references/top-journal-standards.md`：本檔全部落在軸 A（識別）與軸 B（穩健性）。

---

## 一、通用層（所有識別策略都要）

| 等級 | 項目 | 審稿人會怎麼問 | R 套件／函式 | 報告方式 |
|---|---|---|---|---|
| 必做 | 標準誤叢集層級＝處理指派層級 | "Treatment varies at the industry level; why are SEs clustered at the firm level?" | `fixest::feols(..., cluster = ~ind)`；雙向 `cluster = ~firm + year`；依據 Abadie, Athey, Imbens & Wooldridge (2023, *QJE*)：叢集層級由**抽樣設計與處理指派層級**決定，不是「越高越保守」 | 表註一句，引 Abadie et al. (2023) 說明為何選這一層；主表與備選層級並陳於附錄 |
| 必做 | 叢集數少（約 <50）時的推論 | "With so few clusters, conventional cluster-robust SEs over-reject." | `fwildclusterboot::boottest()`（wild cluster bootstrap） | 附錄表，報 bootstrap p 值 |
| 必做 | 替代衡量（X 與 Y 各至少一種） | "Are results sensitive to how you measure X?" | 同主模型重估 | 附錄表，一欄一種衡量 |
| 必做 | **核心構念定義敏感度**（家族企業、集團、ESG 等「定義即結果」的構念） | "Is 'family firm' the TEJ ultimate-controller flag or your own rule? 10% or 20%? Founder or descendant? Would Villalonga and Amit's definition give the same answer?" | 至少三種定義 × 兩個門檻重估主模型（家族企業：Villalonga & Amit, 2006, *JFE* 的創辦人／後代／家族 CEO 區分；Yeh, Lee & Woidtke, 2001, *International Review of Finance* 的台灣控制門檻定義；Claessens, Djankov & Lang, 2000, *JFE* 的最終控制者追溯法；三種定義各對到哪個 TEJ 欄位用 `tej-variable-mapper` 映射，名稱式、不填代碼）；TEJ 最終控制者為資料庫演算法，抽 50 家人工核對並報一致率 | 附錄「定義 × 門檻矩陣表」：列＝定義、欄＝門檻，每格報主係數符號與量級（不是只報星號）；正文一句報「主結果在 k/6 種設定下符號一致」 |
| 必做 | **壞控制變數**（受處理影響的控制變數） | "You control for ROA, but ROA is the channel through which ESG affects Tobin's Q." "Foreign ownership responds to disclosure—why is it on the right-hand side?" | 逐一列出每個控制變數「是否可能受處理影響」（處理後變數＝bad control；Cinelli, Forney & Pearl, 2024, *Sociological Methods & Research*，已查證 2026-09-20）；受影響者**移除後重估**，或改用處理前一期固定值（DiD 的 `xformla` 一律如此，見 `estimator-playbook.md`） | 附錄表：含壞控制／不含壞控制／處理前固定值三欄並陳；正文一句說明哪些控制變數被判定為處理後變數與理由 |
| 必做 | 替代樣本（剔除金融業／單一年度／極端值處理方式） | "Is the effect driven by a subset of firms or years?" | 同主模型重估；`DescTools::Winsorize()` 換 1%／2.5% | 附錄表 |
| 必做 | 證偽檢定：對不該受影響的結果變數做同樣估計 | "A placebo outcome that should not respond would strengthen the design." | 同主模型換 Y | 正文一段＋附錄表 |
| 必做 | 遺漏變數敏感度（至少一種） | "How much selection on unobservables would be needed to explain away the effect?" | Oster (2019) δ：`robomit::o_delta()`（Stata `psacalc`）；Cinelli & Hazlett (2020)：`sensemakr::sensemakr()`、`robustness_value()`、`ovb_contour_plot()` | 正文一句報 δ 或 RV，等高線圖放附錄 |
| 加分 | 隨機化推論（置換檢定） | "Given the small number of treated units, is the p-value reliable?" | 手刻：隨機重排處理指派、`fixest` 重估 1,000 次、算置換 p 值 | 附錄直方圖＋置換 p 值 |
| 加分 | 多重結果變數的多重檢定校正 | "You test six outcomes; which survive correction?" | 報校正後 p 值，方法擇一並引用原文 | 表註 |
| 加分 | 設定曲線（specification curve） | "How many of the reasonable specifications support your result?" | Simonsohn, Simmons & Nelson (2020, *Nature Human Behaviour*)：列出所有合理的設定選擇（衡量、樣本、控制變數、叢集）並全部估計；R `specr` | 附錄圖：估計值依大小排序＋下方設定指示矩陣；正文一句報「k% 的設定與主結果同號且顯著」 |
| 情境觸發 | 係數穩定性（加控制變數後 β 與 R² 的變化） | "Coefficient stability without R² movement is uninformative." | `robomit::o_beta()` 系列 | 附錄表 |

Oster (2019) 的報告紀律：δ 要與 R_max 的假設一起報（例：R_max = 1.3 × R̃），
不能只寫「δ > 1」。Cinelli & Hazlett (2020) 的 RV 要說明「與哪個已觀測控制變數等強的
干擾因子」作為基準（`benchmark_covariates =`），否則審稿人無法判斷 RV 大小的意義。

---

## 二、差異中之差異（含交錯採用）

| 等級 | 項目 | 審稿人會怎麼問 | R 套件／函式 | 報告方式 |
|---|---|---|---|---|
| 必做 | Goodman-Bacon (2021) 分解 | "What share of the TWFE estimate comes from forbidden comparisons?" | `bacondecomp::bacon(y ~ treat, data, id_var, time_var)` | 附錄表：各比較型態的權重與估計值 |
| 必做 | 異質穩健估計量至少一個 | "TWFE is biased under staggered adoption with heterogeneous effects." | Callaway & Sant'Anna (2021)：`did::att_gt()` → `did::aggte(type = "dynamic" / "simple" / "group")`；Sun & Abraham (2021)：`fixest::feols(y ~ sunab(first_treat, year) \| firm + year)`；de Chaisemartin & D'Haultfœuille (2020)：`DIDmultiplegt::did_multiplegt()`；Borusyak, Jaravel & Spiess (2024)：`didimputation::did_imputation()` | 主表放一個，其餘附錄並陳 |
| 必做 | 控制組定義兩種都跑 | "Are never-treated firms comparable? What if they are systematically different?" | `did::att_gt(control_group = "nevertreated")` 與 `"notyettreated"` | 附錄表兩欄 |
| 必做 | 事件研究圖＋前期係數聯合檢定 | "Are the pre-period coefficients jointly zero?" | `fixest::iplot()` 草圖；`fixest::wald(model, "year::-")` 對前期係數做聯合 Wald；`did::aggte(type = "dynamic")` 的 `Wpval` | 正文圖：投稿級圖用 `management-figure` 的 `event_study_plot(rel_time, coef, ci_low, ci_high, ref_period = -1, pre_joint_p = …, breakdown_M = …, estimator = "…")`——參考期、處理時點線、前期陰影與圖註「Pre-period joint Wald p = …; robust to M̄ ≤ …」由函式自動產生，估計量名稱進圖註 |
| 必做 | 前趨勢檢定力（Roth, 2022） | "An insignificant pre-trend test may simply be underpowered." | `pretrends::pretrends()`（輸入事件研究係數與 VCV，回報對假設違反的檢定力） | 圖註或附錄：報「以 80% 檢定力能偵測的最小線性違反」 |
| 必做 | 誠實區間（Rambachan & Roth, 2023） | "How large a violation of parallel trends would overturn the result?" | `HonestDiD::constructOriginalCS()`；相對幅度限制 `createSensitivityResults_relativeMagnitudes(Mbarvec = seq(0, 2, 0.5))`；平滑限制 `createSensitivityResults(Mvec = ...)`；`createSensitivityPlot()` | 正文一句報 breakdown 值；表放附錄（模板見第七節） |
| 必做 | 安慰劑—時間 | "Does a fake treatment date k years earlier produce an effect?" | 把 `first_treat` 提前 k 年重估 | 附錄表 |
| 必做 | 預期效應 | "Firms may respond before the effective date." | `did::att_gt(anticipation = 1)`；或以宣布日重新定義處理 | 附錄表；處理定義表放正文 |
| 加分 | Stacked DiD | "A stacked design would be a transparent robustness check." | 手刻：每個採用組配一個乾淨對照窗，堆疊後 `fixest::feols(... \| firm^stack + year^stack)` | 附錄表 |
| 加分 | 組成穩定（平衡 vs 非平衡面板） | "Does entry and exit correlate with treatment?" | 兩種樣本重估 | 附錄表 |
| 加分 | 序列相關（Bertrand, Duflo & Mullainathan, 2004） | "Serially correlated outcomes inflate significance." | 單位層級叢集為基本；壓縮成前後兩期重估 | 表註或附錄 |
| 情境觸發 | 處理強度（dose／連續處理）設計 | "The policy hit everyone; where is the control group?" 追問："Under heterogeneous dose effects, the TWFE dose coefficient is not a causal parameter without strong parallel trends." | 以暴露程度連續變數交乘 `post`；**識別假設比二元 DiD 更強**：`post × dose` 的 TWFE 係數要解讀為因果，需要「強平行趨勢」（各劑量組在**任一**劑量水準下的潛在結果趨勢相同，不只是無處理時的趨勢相同），且劑量效果異質時 TWFE 權重可為負（Callaway, Goodman-Bacon & Sant'Anna, "Difference-in-Differences with a Continuous Treatment"：已查證 2026-09-20，仍為 NBER 工作論文 w32117／arXiv 2107.02637（2021 首發，最近版本 2025），未見期刊版；同作者另有 *AEA Papers and Proceedings* 2024 短文 "Event Studies with a Continuous Treatment"；投稿前**建議查證**是否已刊出，引用以當時最新版本為準；R 套件 `contdid`） | 正文明寫識別假設已改為強平行趨勢（不可再稱古典 DiD）；報告**劑量分組的事件研究**（高／中／低暴露各一條，用 `event_study_plot` 分面或疊圖）與**劑量單調性檢查**（效果是否隨劑量單調變化；非單調要解釋或承認劑量效果異質） |
| 情境觸發 | 溢出效應 | "Could treated firms affect control firms in the same industry?" | 剔除同產業對照或改用產業×年固定效果 `\| firm + ind^year` | 附錄表 |
| 情境觸發 | 三重差分 | "A third difference would tighten identification." | 加入不受影響的第三維度交乘 | 附錄表 |

**攻防表的語言**：控制組用 not-yet-treated 時，攻防表寫「假設尚未採用者未預期調整」；
用 never-treated 時寫「假設永不採用者與採用者在條件平行趨勢下可比」。兩者估計值方向
一致且量級接近＝穩健性的一列；不一致就要解釋，不能只挑好看的報。

**對照組情境表——「兩種都跑」之前先回答審稿人真正會問的四個情境**（台灣制度分批適用的
稿件幾乎每篇都撞到至少兩個；對不上號就別寫「兩種都跑」）：

| 情境 | 審稿人會怎麼問 | 主設定怎麼做 | 穩健性怎麼做 | 稿件哪裡寫 |
|---|---|---|---|---|
| **全體終將受處理**（規定最終適用所有上市櫃公司，最後一批沒有 not-yet-treated 對照） | "Your last cohort has no clean control; how do you truncate the event window?" | 只報**有乾淨對照的 cohort × period** 格子；最後一批的動態效果**不進事件研究圖**，事件窗長度以「最後一批進場前」為上限；`did::att_gt(control_group = "notyettreated")` 後在 `aggte()` 前依 cohort 篩選 | 附錄報「含最後一批、以其進場前期間為對照」的版本，並明寫兩者差異 | 識別策略節一段：哪些 cohort 進主圖、事件窗為何截在 k 期 |
| **門檻分批**（依實收資本額等門檻分批適用，never-treated 就是門檻以下最小的公司） | "You condition on size for parallel trends but size defines treatment—where is the overlap?" | 重疊（overlap）在門檻附近：主設計改為**門檻附近帶寬內的 RDD**（第四節）或**限制樣本至重疊區**（門檻兩側各 k 倍帶寬內的公司）；CS／SA 全樣本估計降為穩健性 | `did` 的 `xformla` 不放定義處理的變數本身（規模）；改用處理前一期的其他共變數；重疊區敏感度（帶寬 ×0.5、×2） | 識別策略節先寫「處理由門檻決定，全樣本條件平行趨勢無法以規模為條件」，再寫主設計 |
| **自願提前者**（法規生效前已自願採用、設置或揭露；always-treated／anticipators） | "Where do voluntary early adopters go? They are the firms most likely to differ." | 主設定**剔除**自願提前者（不進處理組也不進對照組），並報剔除數 | 穩健性另設一個 cohort（以自願採用年為 `first_treat`）重估；或以 `anticipation = 1` 允許一期預期 | 資料節報剔除 N；處理定義表明列「自願提前者：剔除／另設 cohort」 |
| **套件編碼核對**（`did` 與 `fixest::sunab` 對 never-treated 的編碼不同） | "Your Table 3 uses `did` and Table A3 uses `sunab`; are never-treated firms coded consistently?" | `did::att_gt` 的 `gname` 對 never-treated 設 **0**；`fixest::sunab` 的 never-treated 是「cohort 值不在 period 範圍內」的單位（已查證 2026-09-20：fixest 文件的 `base_stagg` 範例以 `year_treated = 10000` 標記 never-treated）。**不要兩套件共用同一欄位**：各建一欄（`g_did` 設 0、`g_sunab` 設 10000 或 `Inf`），並在程式碼加核對——`stopifnot(sum(df$g_did == 0) == sum(df$g_sunab > max(df$year)))` | 對照兩套件的 never-treated 單位數與 ATT 是否同號同量級；不一致先查編碼再查估計量 | 再現性聲明：兩欄的編碼規則各寫一句 |

**判斷是否落在情境二的快速檢查**：把處理指派變數（門檻變數）放進 `xformla` 會不會讓
never-treated 的傾向分數趨近 0？會＝沒有重疊，條件平行趨勢無法以該變數為條件。
`did::att_gt` 若警告 "overlap condition violated" 或傾向分數被修剪（trimmed），就是這個情境。

---

## 三、工具變數

| 等級 | 項目 | 審稿人會怎麼問 | R 套件／函式 | 報告方式 |
|---|---|---|---|---|
| 必做 | 第一階段完整報告 | "Report the first stage, not just the F." | `summary(iv, stage = 1)`；`fixest::fitstat(iv, ~ ivf + ivwald + kpr)`（Kleibergen-Paap） | 正文表：第一階段係數、F、KP 統計量 |
| 必做 | 弱工具穩健推論 | "With a weak first stage, 2SLS confidence intervals are unreliable." "F > 10 is not a valid threshold for inference." | Montiel Olea & Pflueger (2013) effective F；Anderson-Rubin 信賴區間：`ivmodel::AR.test()`；`ivreg::ivreg(..., diagnostics = TRUE)` 的弱工具診斷；**tF 程序**（Lee, McCrary, Moreira & Porter, 2022, *AER*）：依第一階段 t 值調整 2SLS 的臨界值，單一工具時是頂刊現行標準——「F > 10 經驗法則已不被接受」，F 約 10 時 tF 校正後的 95% CI 遠寬於傳統 CI | 表註報 effective F 與 tF 校正後的 CI（單一工具）；AR 區間放附錄 |
| 必做 | 縮減式（reduced form） | "Show the reduced form; the IV estimate should be interpretable from it." | `fixest::feols(y ~ instrument + controls \| FE)` | 附錄表 |
| 必做 | OLS 與 IV 並陳並解釋偏誤方向 | "Why is the IV estimate larger than OLS? That is inconsistent with your story of upward bias." | 同表兩欄；Jiang (2017), "Have instrumental variables brought us closer to the truth," *Review of Corporate Finance Studies* 6(2), 127–140（已查證 2026-09-20，Oxford Academic 頁面）指出財務文獻中 IV 估計值普遍大於 OLS，與「OLS 向上偏誤」的敘事矛盾，審稿人會直接引這篇 | 正文一段解釋方向：若 IV > OLS，必須給出衡量誤差衰減或 LATE 順從者效果較大的具體論證，不能略過 |
| 必做 | 排除限制的制度論證 | "Why would the instrument affect Y only through D?" | 無統計檢定；逐一列出其他管道並用制度或資料排除 | 攻防表「只可論證」列 |
| 加分 | 「近似外生」敏感度（Conley, Hansen & Rossi, 2012） | "How much direct effect of the instrument on Y can be tolerated?" | Stata `plausexog`；R 需手刻 | 附錄圖 |
| 加分 | 過度識別檢定（僅多工具時） | "Hansen J passes, but that assumes at least one instrument is valid." | `fixest::fitstat(iv, ~ sargan)` | 表註，並註明檢定的侷限 |
| 情境觸發 | LATE 解釋與順從者描述 | "Who are the compliers? Is the LATE policy-relevant?" | 順從者特徵表（Kappa 加權） | 附錄表 |
| 情境觸發 | 移位—份額（shift-share）工具 | "Exposure shares may themselves be endogenous." | 依 Borusyak, Hull & Jaravel (2022) 或 Goldsmith-Pinkham, Sorkin & Swift (2020) 的架構擇一論證 | 正文說明識別來源是份額還是衝擊 |

---

## 四、斷點迴歸

| 等級 | 項目 | 審稿人會怎麼問 | R 套件／函式 | 報告方式 |
|---|---|---|---|---|
| 必做 | 操縱檢定 | "Can firms sort around the threshold?" | `rddensity::rddensity(running, c = cutoff)`；McCrary (2008) | 正文圖＋p 值 |
| 必做 | 頻寬敏感度 | "Results should not hinge on one bandwidth." | `rdrobust::rdbwselect()`；主頻寬 ×0.5、×2 重估 `rdrobust::rdrobust(y, x, c, h = ...)` | 附錄表或圖（估計值對頻寬） |
| 必做 | 多項式階數與核函數 | "Higher-order polynomials can create spurious jumps." | `rdrobust(..., p = 1)` 與 `p = 2`；`kernel = "triangular"` 與 `"uniform"` | 附錄表 |
| 必做 | 共變數在門檻的連續性 | "Do predetermined covariates jump at the cutoff?" | 對每個共變數跑 `rdrobust()` | 附錄表 |
| 必做 | 安慰劑門檻 | "Is there a jump at fake cutoffs?" | 在門檻兩側的非真門檻重估 | 附錄圖 |
| 加分 | 甜甜圈 RDD | "Observations right at the cutoff may be manipulated." | 剔除 ±ε 後重估 | 附錄表 |
| 加分 | 局部隨機化推論 | "With few observations near the cutoff, asymptotics are questionable." | `rdlocrand::rdrandinf()` | 附錄表 |
| 情境觸發 | 模糊 RDD 的第一階段 | "How sharp is compliance at the threshold?" | `rdrobust(..., fuzzy = D)`；報第一階段跳躍 | 正文表 |

---

## 五、合成控制

| 等級 | 項目 | 審稿人會怎麼問 | R 套件／函式 | 報告方式 |
|---|---|---|---|---|
| 必做 | 前期擬合品質 | "Pre-treatment RMSPE is large; the synthetic unit is not a credible counterfactual." | `Synth::dataprep()` → `Synth::synth()` → `Synth::synth.tab()` | 正文圖＋前期 RMSPE |
| 必做 | 供體池理論化 | "Why these donors? Donors that were themselves affected contaminate the counterfactual." | 供體篩選規則寫進正文 | 正文一段＋附錄供體清單與權重 |
| 必做 | 空間安慰劑（置換） | "Is the treated unit's gap unusual relative to placebo gaps?" | 每個供體輪流當假處理；`tidysynth::plot_placebos()`；報 post/pre RMSPE 比的排名 | 正文圖（所有 gap 疊圖）＋排名 p 值 |
| 必做 | 時間安慰劑 | "Does a fake treatment date produce a gap?" | 把處理年提前重跑 | 附錄圖 |
| 加分 | 留一法（leave-one-out donors） | "Is the result driven by a single donor with a large weight?" | 逐一剔除高權重供體重跑 | 附錄圖 |
| 加分 | 增強型合成控制 | "Bias from imperfect pre-fit can be corrected." | `augsynth::augsynth()`（Ben-Michael, Feller & Rothstein, 2021） | 附錄表 |
| 加分 | 合成 DiD（synthetic DiD） | "With several treated units and a long panel, SDID would be more robust than either SCM or DiD alone." | Arkhangelsky, Athey, Hirshberg, Imbens & Wager (2021, *AER*)：同時對單位與時期加權，前期擬合不完美時比 SCM 穩健、單位不可比時比 DiD 穩健；R `synthdid::synthdid_estimate()`，推論用 `vcov(..., method = "placebo")` 或 `"bootstrap"` | 附錄表：SCM／DiD／SDID 三欄並陳；多處理單位、面板較長（T ≥ 10）時可升為主表 |
| 情境觸發 | 多處理單位 | "With several treated units, how are effects aggregated?" | `augsynth` 的多單位設定或 `Synth` 逐一估計後平均 | 正文說明 |

Abadie (2021) 的建議是把權重表放正文：權重稀疏且集中在少數同質供體，才有可信度。

---

## 六、短窗事件研究（市場反應；台灣公開資訊觀測站事件）

| 等級 | 項目 | 審稿人會怎麼問 | R 套件／函式 | 報告方式 |
|---|---|---|---|---|
| 必做 | 事件日精確性 | "Announcements after market close should be assigned to the next trading day." "What about events whose fact date precedes the announcement date?" | 事件檔建構走 `public-disclosure-scout` Step 2：t = 0 以發言日期＋時間戳為準（13:30 後→次一交易日）；事實發生日另存 `fact_date`，早於發言日期者檢查事前異常報酬（資訊外洩）並另報以事實發生日為 t = 0 的版本 | 資料節一段＋附錄表（兩種 t = 0 的 CAR 並陳） |
| 必做 | 混淆事件篩查 | "Were there other announcements in the event window?" | 以同公司 ±k 日的其他重大訊息篩除或標記 | 資料節＋附錄剔除清單 |
| 必做 | 事件窗與估計窗敏感度 | "Why (−1, +1)? Show (−3, +3) and (−5, +5)." | 多窗重估 | 附錄表 |
| 必做 | 期望報酬模型敏感度 | "Market model vs. factor model." | 市場模型為主；因子模型需台灣因子資料（來源與建構要交代） | 附錄表 |
| 必做 | 事件日重疊（日曆叢集）與橫斷面相關 | "Events cluster in time; standard tests over-reject." | Boehmer, Musumeci & Poulsen (1991) 標準化檢定；Kolari & Pynnönen (2010) 校正 | 表註註明檢定 |
| 加分 | 無母數檢定 | "Returns are non-normal; report a rank or sign test." | Corrado (1989) 秩檢定 | 表中並列 |
| 情境觸發 | 小型股薄交易 | "Thin trading biases beta." | Scholes–Williams 型調整或剔除交易日不足樣本 | 附錄表 |
| 情境觸發 | CAR 的橫斷面迴歸 | "Standard errors should account for event-date clustering." | `fixest::feols(car ~ x, cluster = ~event_date)` | 正文表 |

---

## 七、台灣商管稿件在頂刊的常見落差→具體對策

三個落差在識別層的表現與對策。落差 1 與 3 在 `q1-journal-reviewer` 的
`references/top-journal-standards.md` 第五節有完整版；這裡只寫**識別策略節**要做的部分。

### 落差 1：情境複製——讓穩健性矩陣證明「台灣制度特徵在做識別的工作」

- **表現**：識別策略節寫「以台灣上市櫃公司為樣本進行 DiD」，制度特徵只是背景。
- **對策（第 4 節識別策略）**：把制度特徵寫成**處理變異的來源**，並用異質性分析證明
  機制來自該特徵。句式：
  > "Identification comes from [institutional feature], which generates variation in D that is
  > plausibly unrelated to Y for reasons of [institutional logic]. If the mechanism operates
  > through [feature], the effect should be stronger among firms with [high exposure to feature]."
- **附表**：異質性表以「制度特徵的暴露程度」分組（例：控制權與盈餘分配權偏離高／低；
  是否受某分批規定影響），`did::aggte(type = "group")` 或交乘項。這張表同時回答軸 B
  的機制區辨與軸 D 的「為什麼是台灣」。

### 衝擊品質六問：「以 X 法規為外生衝擊」夠不夠格（落差 2 的前置檢核）

財務家族審稿人（JFE／JCF／RFS）對「制度變革當自然實驗」的第一輪問題不是平行趨勢，
而是 **Atanasov & Black (2016, *Critical Finance Review*)** 的衝擊品質清單：這個衝擊夠不夠
強、夠不夠外生、是否只透過處理影響結果、受影響者是否如同隨機、共變數是否平衡、有沒有
被預期。家族原本只覆蓋其中的預期效應與平行趨勢；下表把六問各對到台灣四種常見設計，
每格是**可直接寫進第 4 節識別策略的論證句＋對應檢定**（年度、門檻、公告文號一律以主管
機關公告為準，論文須引公告；本表不填具體數字）。六問掛在下方「台灣常見設計→對應策略」
表之上，不取代它。

| 六問 | 審稿人怎麼問 | 資本額分批適用 | 治理機制分批強制 | 準則全面轉換 | 評等／評鑑公布 |
|---|---|---|---|---|---|
| **1. 衝擊強度**（處理真的改變了行為嗎） | "Did the rule actually bind, or were firms already complying?" | 論證：「規定生效前，門檻以上公司自願揭露率為 x%，生效後為 y%」＋檢定：第一階段（處理指派→實際揭露）的跳躍幅度；`fixest::feols(disclose ~ treat \| firm + year)` 報 first-stage 係數 | 論證：「生效前已自願設置者 N 家（占 z%），主設定剔除」＋檢定：設置率在生效年的斷點 | 論證：「轉換使 Y 的衡量從 A 準則變為 B 準則，差異集中於〔科目〕」＋檢定：暴露程度（受影響科目占比）的橫斷面變異夠大（報分位數） | 論證：「評等首次公布日前市場無法取得該資訊」＋檢定：公布日 CAR 顯著異於零（第六節） |
| **2. 外生性**（衝擊來源與結果無關） | "Was the policy a response to the very outcome you study?" | 論證：「門檻由主管機關依〔公告年〕設定，適用範圍以法規生效前一年度實收資本額為準，公司無法在公告後調整實收資本額以規避」＋檢定：`rddensity::rddensity(capital, c = threshold)` 門檻附近堆積檢定；公告前後增資／減資頻率是否異常 | 論證：「分批依據為公司屬性（如產業別、資本額），非依 Y 的表現」＋檢定：處理指派對處理前 Y 水準與趨勢的迴歸不顯著 | 論證：「轉換為國際準則接軌之全國性政策，非針對特定產業或公司表現」；**弱點要明寫**：全體同時適用＝無對照組，識別依賴暴露程度（見第二節劑量設計的強平行趨勢） | 論證：「評等由第三方機構依公開資訊計算，公司無法在公布前得知名次」＋檢定：名次門檻附近的操縱檢定（第四節） |
| **3. 只透過處理影響結果**（only-through／排除限制） | "Could the rule affect Y through channels other than D?" | 論證：「同一公告未同時變更其他義務」；若同批公告含多項規定，明列並論證其他規定不影響 Y | 論證：「機制設置為唯一變更；同期其他治理規定〔列出〕適用範圍不同，可用差異區分」＋檢定：對不受該機制影響的結果做證偽（通用層） | **最難過的一問**：準則轉換同時改變 Y 的衡量與公司行為；論證只能寫「本文研究的是衡量變更本身的效果／行為效果」擇一，不可混稱 | 論證：「公布只改變資訊集，不改變公司基本面」＋檢定：公布窗內無其他公司公告（第六節混淆事件篩查） |
| **4. 受影響者如同隨機**（處理指派與潛在結果無關） | "Treated firms are the large ones; how is that as-if random?" | 論證：「門檻附近的公司在門檻兩側如同隨機」——**只在門檻附近成立**，全樣本不成立；主設計改門檻 RDD 或重疊區（第二節對照組情境表情境二） | 論證：「分批順序由公告決定，公司無法選擇批次」＋檢定：批次與處理前特徵的平衡表 | 不成立（全體受處理）；改以暴露程度的「如同隨機」論證：暴露程度由歷史科目結構決定，非公司對轉換的預期反應 | 論證：「名次門檻兩側的公司在門檻附近如同隨機」＋檢定：門檻兩側共變數連續性（第四節） |
| **5. 共變數平衡** | "Show me the balance table." | 處理前一期特徵在門檻兩側（帶寬內）的平衡表；全樣本不平衡要承認 | 各批次處理前特徵平衡表；不平衡的變數進 xformla（處理前固定值） | 高／低暴露組處理前特徵平衡表；不平衡＝強平行趨勢可疑 | 名次門檻兩側平衡表 |
| **6. 無預期** | "Firms knew this was coming; did they adjust before the effective date?" | 論證：「公告日至生效日間隔 k 個月；以公告日重新定義處理作穩健性」＋檢定：`did::att_gt(anticipation = 1)`；事件研究前期最後一期係數 | 同左；另加「自願提前者剔除」（對照組情境表情境三） | 論證：「轉換時程於〔年〕公告，公司可能提前調整會計政策」＋檢定：公告至生效期間 Y 的趨勢是否已變 | 論證：「評等公布日固定且事先公告，但名次本身不可預期」＋檢定：公布前 k 日的異常報酬（資訊外洩檢查） |

**寫法紀律**：六問每一問在識別策略節至少一句；答不了的（例：準則全面轉換的第 3、4 問）
**明寫答不了**並說明識別依賴什麼替代假設，比假裝答了更能過審。相關文獻：
Baker, Larcker & Wang (2022, *JFE*) 是財務審稿人引用交錯 DiD 問題的標準文獻；
Roth, Sant'Anna, Bilinski & Poe (2023, *Journal of Econometrics*) 是現代 DiD 的總覽——
兩者與 Atanasov & Black (2016) 的完整引用見 `method-and-software-citations.md`。

### 落差 2：識別靠制度變革或公開資訊觀測站事件，但平行趨勢只畫圖、沒做誠實區間

- **表現**：常見的台灣「自然實驗」——揭露規定依實收資本額或產業分批適用、治理機制
  強制設置分批、會計準則全面轉換、評等或評鑑結果公布——各有專屬威脅，但稿件一律
  用「TWFE＋一張大致平行的圖」處理。
- **對策：先對號入座，再做專屬必做項**（年度與門檻一律以主管機關公告為準，論文須引公告文號）：

  | 台灣常見設計 | 對應策略 | 專屬必做項（本檔哪一節） |
  |---|---|---|
  | 規定依實收資本額門檻分批適用 | 交錯 DiD（第二節）或門檻 RDD（第四節）；never-treated＝門檻以下公司時重疊不足，主設計改門檻附近 RDD 或重疊區（第二節對照組情境表情境二） | 門檻附近操縱檢定（實收資本額是否有堆積，`rddensity`）；預期效應（自願提前揭露者→剔除，情境三）；同產業溢出；全體終將適用時最後一批不進動態圖（情境一） |
  | 治理機制依公司屬性分批強制 | 交錯 DiD（第二節） | never-treated 的定義：自願先設置者主設定剔除、穩健性另設 cohort（第二節對照組情境表情境三）；Goodman-Bacon 分解；宣布日 vs 生效日；`did` 與 `sunab` 的 never-treated 編碼分欄（情境四） |
  | 準則或制度全面同時轉換 | 處理強度設計（第二節情境觸發） | 明寫識別假設已改為**強平行趨勢**（各劑量組在任一劑量下趨勢相同）；報劑量分組事件研究與劑量單調性；不可再稱古典 DiD |
  | 評等、評鑑結果公布 | 短窗事件研究（第六節）或名次門檻 RDD（第四節） | 混淆事件篩查；名次附近的操縱與共變數連續性 |

- **誠實區間的報告模板**（正文一段＋附錄一表，缺一不可）：

  > "Figure X reports event-study coefficients with 95% confidence intervals; pre-period
  > coefficients are jointly insignificant (Wald p = [value]). Because such tests can be
  > underpowered (Roth, 2022), we report that our design would detect a linear pre-trend of
  > [slope] with 80% power. Following Rambachan and Roth (2023), Table Y shows that the
  > estimate remains bounded away from zero for post-treatment violations up to M̄ = [value]
  > times the largest pre-treatment deviation (breakdown value M̄* = [value])."

  | 限制型態 | 參數值 | 穩健 CI 下界 | 上界 | 排除零？ |
  |---|---|---|---|---|
  | 相對幅度 M̄ | 0 / 0.5 / 1 / 1.5 / 2 | … | … | … |
  | 平滑 M | 0 / 0.01 / 0.02 / 0.05 | … | … | … |
  | Breakdown | M̄* = … | — | — | — |

  資料節同時交代 TEJ 特有威脅：欄位回填（以資料庫「首次揭露日」而非「最新值」建構
  處理時點）、下市公司是否保留、會計年度對齊。交錯採用時主表估計量名稱要進表頭。

### 落差 3：只報統計顯著——處理效應的經濟量級要有分母與基準

- **表現**：報 ATT = 0.021***，不說 0.021 是什麼單位、相對誰而言。
- **對策（結果節主表後）**：ATT 一律以「處理組處理前平均數的百分比」報一次、以「Y 的
  標準差」報一次，並給一個可比基準（同構念他國估計、家族 vs 非家族差距、產業中位數）。
  事件研究的 CAR 同時報基點與以市值換算的金額。
- **句式**：
  > "The ATT of [value] corresponds to [p]% of the treated firms' pre-treatment mean
  > ([m]% of a standard deviation), a magnitude [comparable to / smaller than] the estimate of
  > [Author, Year] in [setting]."
- **附表**：經濟量級與基準表（欄位模板見 `q1-journal-reviewer` 的
  `references/top-journal-standards.md` 第五節落差 3）。基準數值指不回出處就不放。

---

## 八、正文 vs 附錄的擺放清單（投稿前對照）

| 放正文 | 放附錄（Internet／Online Appendix） |
|---|---|
| 識別策略節：變異來源、反事實、關鍵假設、處理定義表 | 完整 Goodman-Bacon 分解表 |
| 事件研究圖（含 CI、前期聯合檢定 p 值、breakdown 值） | 誠實區間表、前趨勢檢定力表 |
| 主估計量（名稱進表頭）＋一個異質穩健估計量 | 其餘估計量並陳表、控制組兩種定義表 |
| 經濟量級段＋至少一個基準 | 替代衡量、替代樣本、winsorize 層級表 |
| 證偽檢定一段 | 安慰劑—時間、安慰劑—單位完整表 |
| 遺漏變數敏感度一句（δ 或 RV） | 等高線圖、係數穩定性表 |

攻防表（SKILL.md Step 5）每一列的「你的證據」欄，直接填本檔的表號；審稿人問到時，
回覆信引用同一表號（`response-letter-craftsman` 的
`references/rr-conventions-top-journals.md` 有對應的回覆句式）。
