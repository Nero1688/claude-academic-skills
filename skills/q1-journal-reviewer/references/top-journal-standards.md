# 頂刊審稿人硬期待：依期刊家族 × 四軸

本檔延伸 SKILL.md 的五個審查維度，把它們壓成審稿人實際用來判生死的**四軸**，
並依兩個期刊家族分列「沒有就退」門檻與「有但薄」的常見審稿語。用途有二：
(1) 你扮演 Reviewer 2 寫報告時，Major Concerns 的嚴重度要對得上這裡的門檻；
(2) 使用者投稿前自我診斷，知道哪一軸是這個家族的第一刀。

| SKILL.md 維度 | 本檔四軸 | 說明 |
|---|---|---|
| 維度 1 理論貢獻定位 | 軸 D 理論貢獻 | 含機制的理論化 |
| 維度 2 識別策略與內生性 | 軸 A 識別策略 | 頂刊第一刀 |
| 維度 3 穩健性＋維度 4 機制檢驗 | 軸 B 穩健性（含機制區辨） | 穩健性矩陣本體見 `causal-inference-architect` 的 `references/robustness-battery.md` |
| 維度 5 經濟顯著性 | 軸 C 經濟量級 | 財務家族幾乎是必要條件 |

誠實防線：本檔**不提供**任何期刊的接受率、影響係數、審稿天數或編輯姓名——
那些查無公開可靠來源，工具寧可不寫。凡涉及期刊政策（字數、附錄、匿名規定），
一律以該刊當期作者指南為準；本檔只寫審稿人的**期待**，不寫期刊的**規定**。

---

## 一、兩個家族的審稿文化差異（先知道誰在讀你的稿）

| 面向 | 管理類（AMJ／AMR／SMJ／JOM／Organization Science） | 財務治理類（JFE／JF／RFS／JCF；CGIR 為混合型，見表後註） |
|---|---|---|
| 審稿人是誰 | 多為理論家＋方法學者的組合；第一刀常是「理論貢獻夠不夠」 | 多為應用計量學者；第一刀幾乎必是「變異來源是否外生」 |
| 假說的角色 | 假說要從**機制**推出，且假說之間要有理論張力（不是一串正相關） | 假說常寫成「區辨假說」（hypothesis A vs B），重點在能否用資料區分兩個機制 |
| 內生性的容忍 | 接受「多管齊下」（FE＋Heckman＋PSM＋IV 並陳）作為誠實努力，但要明講各法的極限 | 期待**一個**可信的準實驗；多管齊下但每管都弱，會被讀成「沒有識別」 |
| 附錄慣例 | 補充材料常見但正文要自足；機制證據不能只在附錄 | Internet／Online Appendix 是常態，穩健性矩陣放附錄、正文只留主表與關鍵敏感度 |
| 顯著性語言 | 部分期刊作者指南已要求以係數、標準誤與信賴區間為主、淡化星號並報效果量（以該刊當期作者指南為準）；依據是 Bettis, Ethiraj, Gambardella, Helfat & Mitchell (2016, *SMJ*) 的編輯聲明——要求報告效果量、信賴區間，並對「僅以 p < .05 為證據」的做法明確表態 | 星號仍常見，但經濟量級段是必要條件；t 值置於括號內。經濟量級的寫法可引 Mitton (2024), "Economic significance in corporate finance," *Review of Corporate Finance Studies* 13(1), 38–79（已查證 2026-09-20）——該文調查頂級財務期刊 2000–2018 年 604 篇論文，指出「以應變數均值為分母」的量級寫法有理論與實證缺陷，第五節落差 3 的基準表要求同時給標準差與可比基準即是回應此點 |
| 對台灣單國樣本的態度 | 問「理論上為什麼是台灣」；情境要能轉成邊界條件 | 問「制度變異能否被利用來識別」；情境要能轉成識別優勢 |
| AMR 特例 | AMR 為純理論期刊，軸 A／B／C 不適用；軸 D 標準更高——要提出新構念、新關係或新機制，而非「整理」既有理論 | — |

**CGIR 註（審稿經驗判斷，非期刊政策）**：CGIR 的審稿文化偏管理——理論貢獻優先、接受多方法
並陳——把它與 JFE／JF／RFS 同列「期待一個可信準實驗、多管齊下＝沒有識別」的家族，會誤導使用者
把 CGIR 稿件過度計量化。本檔把 CGIR 視為**混合型**：**軸 D（理論貢獻）依管理家族**的門檻審、
**軸 A（識別策略）依財務家族「有但薄」欄**審（有一個可信設計即可，不要求 JFE 級的準實驗，
但 FE＋PSM 並陳而各法極限未講仍是 Major）。軸 B、C 兩家族取其嚴者。此為審稿經驗判斷，
投稿前以該刊當期作者指南與近三年刊出論文的方法為準。

---

## 二、管理類家族：四軸門檻

| 軸 | 沒有就退（Fatal） | 有但薄（Major）的典型樣態 | 審稿人常見用語（英文原句＋意思） |
|---|---|---|---|
| A 識別策略 | 核心自變數明顯內生，全文連討論都沒有；或只跑 OLS／FE 就宣稱「效果」 | 只用一種方法（例如只 PSM）；Heckman 沒有排除變數；IV 沒有論證排他性；把「加了公司固定效果」寫成「已解決內生性」 | "The identification strategy does not rule out reverse causality." ＝ 你的變異來源說不清。"Fixed effects do not address time-varying omitted variables." ＝ FE 被高估了 |
| B 穩健性與機制 | 主結果只有一個設定；或提出的機制與競爭解釋完全沒區辨 | 穩健性表很多，但沒有一張對應「最致命的那個威脅」（robustness theater）；機制只靠故事，沒有中介或異質性證據；調節效果沒畫邊際效果圖、沒報顯著區間 | "The results are consistent with the hypothesis but equally consistent with [alternative]." ＝ 沒排除競爭解釋。"The mechanism is asserted rather than tested." ＝ 黑箱沒打開 |
| C 經濟量級 | 管理類較少單獨因此退稿，但與 A／D 疊加時會被寫進退稿理由 | 只有一句 "practically significant" 沒有數字；交互作用只報係數，沒有 simple slopes 或 Johnson–Neyman 區間；大樣本下三顆星被當成證據強度 | "What is the practical magnitude of this effect?" ＝ 請換算。"With this sample size, significance is uninformative." ＝ 別靠星號 |
| D 理論貢獻 | 貢獻句找不到；假說是「X 與 Y 正相關」而無理論張力；理論只出現在「drawing on agency theory」這一句 | 貢獻是「首次在台灣檢驗」；補一個調節變數但說不出它揭露了什麼新機制；理論推導與假說斷裂（假說不是從機制推出來的）；邊界條件沒有講 | "The contribution is incremental." ＝ 讀者學不到新東西。"It is not clear what we learn beyond [prior paper]." ＝ 你沒有定位差異。"The hypotheses read as a list of expected relationships rather than a theory." ＝ 沒有理論 |

---

## 三、財務治理類家族：四軸門檻

| 軸 | 沒有就退（Fatal） | 有但薄（Major）的典型樣態 | 審稿人常見用語（英文原句＋意思） |
|---|---|---|---|
| A 識別策略 | 沒有可信的外生變異卻宣稱因果；交錯採用只報 TWFE；平行趨勢連圖都沒有 | DiD 沒有事件研究圖；IV 的第一階段 F 未報或明顯偏弱；平行趨勢只畫圖不做敏感度；控制組定義不明（誰是 never-treated？）；標準誤叢集層級與處理層級不一致（處理在產業層級卻只叢集在公司） | "The parallel trends assumption is asserted rather than examined." ＝ 沒做誠實區間。"What is the source of exogenous variation?" ＝ 沒有識別。"Standard errors should be clustered at the level of treatment assignment." ＝ 推論層級錯了 |
| B 穩健性與機制 | 主結果對合理的替代設定翻轉而作者未揭露；沒有任何安慰劑或證偽檢定 | 只報對作者有利的設定；沒有 falsification test（對不該受影響的結果變數做同樣估計）；沒有異質性分割來區辨機制（cross-sectional splits）；穩健性與機制混在同一節 | "The robustness checks are extensive but do not address the main concern." ＝ 做錯方向。"A placebo test on an unrelated outcome would be informative." ＝ 缺證偽 |
| C 經濟量級 | 主結果完全沒有經濟量級討論——在這個家族幾乎是必要條件 | 只換算一次、沒有可比基準；效果大得不合理卻沒解釋；用 R² 變化當經濟意義；把「一單位變動」當量級（一單位是什麼？） | "The authors should discuss economic significance." ＝ 必補。"The implied effect is implausibly large." ＝ 你的估計可能有問題。"How does this compare with prior estimates?" ＝ 缺基準 |
| D 理論貢獻 | 純描述（"we document that…"）而無區辨假說；動機只有「台灣很有趣」 | 兩個機制都能解釋主結果，沒有設計 horse race；「貢獻」寫的是資料新而非知識新；沒有說明為何既有美國證據無法回答這個問題 | "This is a descriptive exercise." ＝ 沒有假說張力。"What do we learn that we did not already know from [U.S. evidence]?" ＝ 情境複製 |

---

## 四、「有但薄」審稿語翻譯表（跨家族通用）

審稿人的客氣句式背後常有明確要求；扮演 Reviewer 2 時用左欄寫、使用者收到時用右欄讀。

| 審稿語 | 真正的意思 | 作者該補什麼 |
|---|---|---|
| "I would encourage the authors to think more carefully about identification." | 目前的識別不可信 | 換策略或加準實驗，不是多加控制變數 |
| "The theoretical framing could be sharpened." | 沒有理論，只有變數 | 重寫引言與假說推導，提出機制 |
| "The single-country setting raises questions about generalizability." | 情境複製 | 制度特徵→理論構念表＋可移植性聲明（第五節對策 1） |
| "Pre-trends look reasonably flat, but…" | 你自己說「大致平行」不算 | 前期聯合檢定＋誠實區間表（第五節對策 2） |
| "It would help to see the economic magnitude." | 這個家族的必要條件 | 經濟量級段＋基準表（第五節對策 3） |
| "The authors may wish to consider [paper X]." | 你漏了關鍵文獻，可能是審稿人自己的 | 引用並實質對話，不是塞進文獻回顧 |
| "The paper is well executed but…" | 執行沒問題，貢獻不夠 | 問題在軸 D，不在方法 |
| "I am not convinced that…" | 這是 Major，不是 Minor | 正面回應，不能只改措辭 |

---

## 五、台灣商管稿件在頂刊的常見落差→具體對策

以下三個落差是台灣（尤其 TEJ 上市櫃 panel）稿件在頂刊最常被殺的位置。每項給：
落差怎麼表現、審稿人怎麼說、對策要改在稿件**哪一節**、用**什麼句式**、附**什麼表**。

### 落差 1：單國樣本被讀成「情境複製」而非理論貢獻

**怎麼表現**：標題寫「以台灣上市櫃公司為例」；引言第一段從「台灣家族企業比例高」起手；
貢獻句是「補足台灣情境的實證缺口」；文獻回顧分「國內文獻／國外文獻」；討論節寫
「未來研究可推廣至其他國家」。這五個訊號任一個出現，審稿人就會寫：

> "This appears to be a replication, in the Taiwanese context, of a well-established finding."
> "The absence of prior Taiwanese evidence is not, by itself, a contribution."

**對策（按稿件位置）**

1. **標題與摘要**：主標題寫機制或理論張力，副標題才放情境（"…: Evidence from Taiwan"）。
   摘要第一句不出現「台灣」；台灣在第三句以「識別優勢」身分出場。
2. **引言第 2–3 段——「識別驅動的情境選擇」句式**（英文投稿用；中文稿對應翻譯）：
   > "Taiwan provides a setting in which [theoretical construct] varies sharply while [confound]
   > is held fixed, because [institutional feature with legal citation]. This allows us to
   > separate [mechanism A] from [mechanism B], which U.S.-based evidence cannot disentangle
   > because [reason]."

   中文對應：「台灣的〔制度特徵〕使〔理論構念〕在〔干擾因素〕固定的條件下產生大幅變異，
   本文據此區分〔機制 A〕與〔機制 B〕——既有美國證據因〔原因〕無法區分兩者。」
3. **第 2 節制度背景——附「制度特徵→理論構念→識別用途」三欄表**：

   | 制度特徵（附法規或文獻出處） | 對應理論構念 | 本文如何利用 |
   |---|---|---|
   | 例：控制權與盈餘分配權偏離普遍（Claessens, Djankov & Lang, 2000） | 代理問題第二型（控制股東 vs 小股東） | 以偏離程度為處理強度 |
   | 例：某項揭露規定依實收資本額分批適用（年度與門檻以主管機關公告為準，論文須引公告） | 外生的揭露成本衝擊 | 門檻兩側比較／分批採用 |

   另附一張「台灣 vs 美國 vs 其他東亞 vs 歐陸」的制度比較表，每列註明出處，
   讓審稿人看到情境是**選出來的**而非**手邊剛好有**。
4. **貢獻句改寫成邊界條件語言**（引言末段與討論節各一次）：
   > "Our findings identify a boundary condition for [theory]: the effect of X on Y reverses
   > when [institutional feature] exceeds [threshold]."

   情境本身變成理論貢獻——這是單國研究在頂刊存活的正規路徑。
5. **討論節——附「可移植性聲明」（portability statement）**：
   > "Our estimates are most likely to generalize to settings characterized by [features];
   > they should not be extrapolated to [settings] because the mechanism requires [condition]."

   搭配一張小表：制度條件 × 預期效果方向，把「限制」寫成「理論預測」。
6. **文獻回顧**：拆掉「國內／國外」結構，改依機制或爭點組織；每一段末句是本文與該爭點的關係。

### 落差 2：識別靠 TEJ 事件或制度變革，但平行趨勢只畫圖、沒做誠實區間

**怎麼表現**：事件研究圖前期係數「看起來大致平行」就過關；用制度變革（強制揭露、
獨立董事規定、會計準則轉換）當外生衝擊，但沒交代宣布日 vs 生效日 vs 首次適用年；
制度變革全體上市櫃同時適用，卻沒說控制組是誰；交錯採用仍只報 TWFE；沒有安慰劑。

> "Pre-treatment coefficients are individually insignificant, but this test has little power."
> "The policy applied to all listed firms; what is the counterfactual?"
> "How would the results change under modest violations of parallel trends?"

**對策（按稿件位置）**

1. **第 4 節識別策略移出附錄放正文**，且含「三件套」：
   (a) 事件研究圖（含 95% 信賴區間、前期係數聯合檢定 p 值）；
   (b) 前趨勢檢定力（Roth, 2022）：報告「本檢定能偵測到的最小違反幅度」；
   (c) 誠實區間（Rambachan & Roth, 2023）：報告 breakdown 值。
   估計細節與 R 函式見 `causal-inference-architect` 的 `references/robustness-battery.md`。
2. **附表模板**——「Table X. Sensitivity of the main estimate to violations of parallel trends」：

   | 限制型態 | 參數 | 穩健信賴區間下界 | 上界 | 是否仍排除零 |
   |---|---|---|---|---|
   | Relative magnitudes | M̄ = 0 / 0.5 / 1 / 1.5 / 2 | … | … | … |
   | Smoothness | M = 0 / 0.01 / 0.02 … | … | … | … |
   | Breakdown 值 | M̄* = … | — | — | — |

3. **句式**：
   > "Under the relative-magnitudes restriction of Rambachan and Roth (2023), the estimate remains
   > bounded away from zero for post-treatment violations of parallel trends up to M̄ = [value]
   > times the largest pre-treatment violation."
4. **制度變革全體同時生效、沒有控制組時**：改用暴露強度（dose）設計或門檻設計（規定依
   實收資本額或產業分批適用者），並在第 4 節附「處理定義表」：宣布日／生效日／首次適用年
   三者擇一為主、其餘兩者做敏感度。TEJ 事件研究的事件日一律以公開資訊觀測站公告日為準
   （事件檔建構走 `public-disclosure-scout`）。
5. **資料節明寫 TEJ 特有威脅**：欄位回填（backfill）造成的前視偏誤、下市公司是否保留
   （存活偏誤）、會計年度與日曆年度對齊方式。交錯採用時附 Goodman-Bacon（2021）分解表，
   讓審稿人看到壞比較佔比。

### 落差 3：只報統計顯著、不報經濟量級與可比基準

**怎麼表現**：「係數顯著為正，支持 H1」；三顆星；上萬筆 firm-year 什麼都顯著；
沒有把係數換成「幾個百分點」或「幾個標準差」；沒有和任何既有估計比較；表格直接貼
統計軟體輸出（五位小數、變數名是資料庫欄位代碼）。

> "With 20,000 firm-year observations, statistical significance is unsurprising."
> "How does this magnitude compare with prior estimates in other markets?"
> "The implied effect seems implausibly large."

**對策（按稿件位置）**

1. **主表之後緊接「經濟量級段」**，固定句式：
   > "A one-standard-deviation increase in X (= [value]) is associated with a [b × s.d.] change
   > in Y, equivalent to [p]% of the sample mean of Y ([m]% of its standard deviation). This
   > magnitude is [comparable to / smaller than / larger than] the estimate of [Author, Year]
   > for [setting] ([value]), which is consistent with [institutional reason]."
2. **附表模板**——「Table X. Economic magnitude of main estimates and benchmarks」：

   | 結果變數 | 係數 | X 的一個標準差 | 隱含 ΔY | 占 Y 平均數 % | 占 Y 標準差 % | 可比基準（出處、情境、數值） | 解讀 |
   |---|---|---|---|---|---|---|---|

3. **可比基準三選一（至少一個）**：文獻基準（同構念在他國的估計）；自然基準（家族 vs
   非家族的平均差距、產業中位數、一年 ROA 的典型波動）；政策基準（法規門檻或主管機關目標值）。
   基準的數值必須指得回出處頁碼，指不回就不寫（硬規則 6）。
4. **顯著性語言紀律**：不寫 "highly significant"；文字用量級、表格才用星號；
   「supports H1」改為 "consistent with H1, with a magnitude of…"；報告信賴區間。
5. **大樣本專屬**：報告最小可偵測效果或信賴區間寬度；當主效果為零時，把「精確估計的零」
   （precisely estimated zero）當成發現來寫，而非「未達顯著」帶過。
6. **表格可讀性**：係數三位小數、標準誤或 t 值置於括號並註明是哪一個、變數名用文字
   而非欄位代碼、每表附「本表在回答什麼問題」的一句話表註。

---

## 六、扮演 Reviewer 2 時如何引用本檔

- Major Concerns 的每一則，標明落在哪一軸；Fatal 必須對得上該家族「沒有就退」欄，
  否則降為 Major。
- 台灣稿件出現第五節的任一落差，報告的「修正路線圖」直接引用對應對策編號
  （例：「落差 1 對策 2、3」），讓使用者知道改哪一節、附哪張表。
- 穩健性缺口不要自己列清單，指向 `causal-inference-architect` 的
  `references/robustness-battery.md` 對應識別策略的矩陣，並註明「審稿人會怎麼問」那一欄。
- 動筆前先過 `references/desk-reject-checklist.md`：若稿件連編輯的 10 分鐘都撐不過，
  五維度的深審沒有意義，報告開頭要先講這件事。
