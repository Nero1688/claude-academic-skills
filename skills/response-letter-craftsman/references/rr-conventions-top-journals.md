# 頂刊 R&R 慣例：分層語氣、矛盾意見、附錄策略、拒絕採納

本檔延伸 SKILL.md Step 1–4 與 `references/letter-templates.md`：那裡給四段式與措辭庫，
這裡給**頂刊層級的程序慣例與策略判斷**——來信怎麼讀、對誰用什麼語氣、做了的分析放哪裡、
什麼時候可以不改。所有期限、版本要求（clean／marked copy）、回覆格式**以該刊來信與
當期作者指南為準**；本檔不寫任何期刊的審查天數、接受率或編輯姓名。

分診用 `python scripts/make_response_matrix.py decision_letter.txt` 先把來信切成逐則意見的
xlsx（欄位：審稿人／編號／意見摘錄／類型／同意度／處理策略／修改位置／狀態），再依本檔決定策略。

---

## 一、先讀懂來信的層級：編輯信是地圖，審稿報告是地形

| 來源 | 它在告訴你什麼 | 你該怎麼用 |
|---|---|---|
| 編輯（或副主編）的信 | 哪些意見是「必須」、哪些是「建議」、哪位審稿人的哪一點決定命運；有時明示風險等級 | 先做編輯點名的；對 editor 的 cover note 依編輯信的順序組織 |
| 審稿人報告的 Major 段 | 若不解決就不會推薦接受的點 | 每一點都要有實質修改，不能只改措辭 |
| 審稿人報告的 Minor 段 | 可快速處理，但零遺漏 | 集中處理、逐點回覆但篇幅短 |
| 審稿人報告的「摘要」段 | 審稿人理解的本文貢獻 | 若他的摘要與你的貢獻句不同，那是寫作問題，優先修 |

常見 R&R 型態（以來信用語為準）：一般 major revision；風險較高的 R&R（編輯信明說
「not guaranteed」「substantial concerns」）；reject-and-resubmit（視為新稿、通常換審稿人）。
三者的回覆信長度與深度不同，但「每則意見必回」的紀律相同。

---

## 二、分層語氣：同一項修改，對編輯與對審稿人寫法不同

| 層 | 讀者要什麼 | 語氣 | 篇幅 |
|---|---|---|---|
| 對編輯的 cover note | 整體策略：主要改了什麼、矛盾怎麼處理、哪些沒改與為什麼 | 精簡、決策者口吻、承認取捨 | 一頁內，3–5 項 |
| 對審稿人的逐點回覆 | 「我的意見被認真對待了嗎、改了沒、改在哪」 | 具體、證據、位置 | 一點一段到一頁 |

**同一修改的兩種寫法**（以「補做異質穩健 DiD 估計量」為例）：
- 對編輯：「依 Reviewer 2 的建議，主結果改以 Callaway & Sant'Anna (2021) 估計量報告，
  TWFE 移至附錄；結論不變，量級略降（§5.1、表 3）。」
- 對審稿人：復述意見 → 「我們同意交錯採用下 TWFE 有偏」→ 做了什麼（Goodman-Bacon 分解
  顯示壞比較占 x%；CS 估計 ATT = …）→ 新文字引用 → 位置（p. 18, §5.1, ll. 4–22；表 3；
  附錄表 A2）。

對編輯**不做的事**：逐點重複審稿人回覆；抱怨審稿人；請編輯「裁決」而不先表態。

---

## 三、矛盾意見的外交處理（三種型態）

| 型態 | 例子 | 處理 | 對編輯的句式 |
|---|---|---|---|
| 方法對立 | R1 要求 IV；R2 認為任何 IV 的排除限制都站不住 | 兩者都做：IV 放附錄並誠實寫排除限制的極限；正文維持準實驗設計 | "Reviewers 1 and 2 offer different views on instrumentation. We report the IV specification in Appendix B with an explicit discussion of the exclusion restriction, while retaining the difference-in-differences design in the main text because [reason tied to identification]." |
| 定位對立 | R1 要更多理論；R2 要砍理論、加實證 | 以編輯信為準；沒有指示時，選與貢獻句一致的方向，並向另一方解釋 | "We have followed the Editor's guidance to [direction]; we explain in our response to Reviewer [X] why this choice serves the paper's contribution." |
| 一方誤解 | R1 認為樣本含金融業（其實已剔除） | 修正措辭讓誤解不可能再發生；對編輯中立說明「已澄清」 | "We have clarified in §3.1 that financial firms are excluded, which addresses Reviewer 1's concern." |

原則：對兩位審稿人各自回覆時，都承認對方觀點的價值；**永遠不在給 A 的回覆裡引述 B
的批評來壓 A**。

---

## 四、「做了但放哪裡」的三層策略

| 層 | 放什麼 | 句式 |
|---|---|---|
| 正文 | 改變結論或量級的分析；編輯點名的分析；主識別策略的必做項 | "We now report … in Table X (p. Y)." |
| 附錄（Internet／Online Appendix） | 不改變結論的穩健性；審稿人要求但讀者不需要細節的分析 | "For completeness, we report … in Internet Appendix Table IA.3 and summarize the result in footnote 12." |
| 只在回覆信 | 審稿人好奇但與貢獻無關、或會拉長正文的分析 | "We conducted this analysis and report it below for the reviewer's reference; we have not included it in the manuscript to preserve focus, but would be glad to add it to the appendix if the Editor prefers." |

「只在回覆信」的風險：審稿人下一輪要求進稿。所以句尾一律留「若編輯認為有助讀者，
可移入附錄」的門。**任何放進回覆信的表，都要與稿件用同一份資料與程式跑出**——
回覆信的數字也受 `thesis-consistency-audit` 的對帳。

---

## 五、每則意見必回、位置精確到頁行

- 編號：R1.1、R1.2…；編輯信的點用 E.1、E.2；審稿人未編號的段落由你編號並在回覆信開頭
  說明「為便於對照，我們將意見依段落編號」。
- 位置格式：頁碼＋節＋行號，並註明以哪個版本為準：
  "p. 12, §4.2, ll. 3–15 (clean version)"。若期刊要求 marked copy，另註 "tracked-changes
  version p. 13"。
- 行號：投稿系統多要求連續行號（以該刊為準）；回覆信定稿前最後一步才填行號，因為改版後
  會漂移（SKILL.md Step 4）。
- 修改對照表（`references/letter-templates.md` 附錄模板）放回覆信末；意見數多時，
  這張表是審稿人第二輪唯一會細讀的東西。
- 「已修改」三個字不能單獨出現：後面必接新文字引用或表號。

---

## 六、拒絕採納的三段式（全信配額 ≤ 2 處）

| 段 | 內容 | 英文句式 | 中文句式 |
|---|---|---|---|
| 1 承認價值 | 說出這個建議會帶來什麼 | "We appreciate this suggestion, which would [benefit]." | 「感謝此建議，它有助於〔益處〕。」 |
| 2 具體理由 | 資料不可得／與識別衝突／會誤導讀者／超出研究問題 | "However, [reason]: [evidence or constraint]." | 「然而〔理由〕：〔證據或限制〕。」 |
| 3 折衷 | 註腳、限制節、附錄、未來研究、部分做法 | "We therefore [partial step], and note this explicitly in [location]." | 「因此我們〔折衷做法〕，並於〔位置〕明示。」 |

**不成立的理由**：篇幅（單獨不成理由）；「其他審稿人沒要求」；「先前文獻也沒做」；
「資料庫沒有這個欄位」（要先查 `tej-data-scout`，確認真的沒有）。
**成立的理由**：該分析需要的識別假設與主設計衝突；該變數在樣本期間內不存在或定義不一致；
該檢定在本設計下沒有檢定力（附計算）。

---

## 七、第二輪與後續輪

- 只回未解決的點，沿用第一輪編號（R2.3 → R2.3 cont.）；已解決的點一行「已於第一輪處理，
  審稿人未再提出」不必重述。
- 不主動開新分析，除非被要求或第一輪承諾過。
- 若第二輪加入新審稿人，對新審稿人完整回覆（他沒看過第一輪）。
- 最後一輪 minor：速度優先；回覆信短，但仍逐點。
- 期限：來信通常載明；需延期時在到期前提出並給具體理由（補做分析所需時間），以該刊為準。

---

## 八、台灣商管稿件在頂刊的常見落差→具體對策（R&R 版）

三個落差在 R&R 階段各有固定的出現方式，回覆策略如下。稿件端的完整改法見
`q1-journal-reviewer` 的 `references/top-journal-standards.md` 第五節，這裡只寫**回覆信怎麼寫**。

### 落差 1：情境複製——審稿人問 "generalizability" 或 "why Taiwan"

- **審稿人常見寫法**："The single-country setting limits generalizability."
  "It is unclear what we learn beyond the Taiwanese context."
- **錯誤回覆**：「台灣是重要的新興市場」「未來研究可擴展至其他國家」——這是承認情境複製。
- **正確回覆結構**：(1) 承認問題；(2) 說明台灣制度特徵**如何做識別的工作**；(3) 新增
  「制度特徵→理論構念→識別用途」表與可移植性聲明；(4) 把發現改寫為邊界條件。
- **句式**：
  > "We agree that the scope of our claims must be stated precisely. Taiwan is not our setting by
  > convenience: [institutional feature] generates variation in [X] that U.S. data cannot provide
  > because [reason]. We now make this explicit in §2 (new Table 1, mapping institutional features
  > to theoretical constructs) and add a portability statement in §6.2 specifying the conditions
  > under which our estimates should and should not generalize (p. 29, ll. 5–18)."

### 落差 2：平行趨勢——審稿人要求誠實區間或質疑前趨勢檢定力

- **審稿人常見寫法**："Pre-trends are visually flat but the test may be underpowered. Please
  report sensitivity to violations of parallel trends (Rambachan & Roth, 2023)."
- **正確回覆結構**：(1) 感謝並同意；(2) 新增前期聯合檢定、Roth (2022) 檢定力、
  誠實區間表（模板在 `causal-inference-architect` 的 `references/robustness-battery.md` 第七節）；
  (3) 正文一句報 breakdown 值，表放附錄；(4) 若結果在小幅違反下就翻轉，**誠實揭露並重新定位**。
- **穩健時的句式**：
  > "Following Rambachan and Roth (2023), we report that the estimate remains bounded away from zero
  > for post-treatment violations up to M̄ = [value] times the largest pre-treatment deviation
  > (new Table A4; summarized on p. 19, ll. 2–6)."
- **不穩健時的句式**（比隱瞞好，且審稿人會尊重）：
  > "The estimate is robust to modest violations (M̄ ≤ [value]) but not to larger ones. We therefore
  > now describe the result as 'consistent with' rather than 'establishing' a causal effect, and
  > we add the complementary evidence from [placebo / heterogeneity] that supports the mechanism
  > (§5.3)."

### 落差 3：經濟量級——審稿人說 "discuss economic significance"

- **審稿人常見寫法**："With 20,000 firm-years, significance is unsurprising; what is the
  economic magnitude, and how does it compare with prior estimates?"
- **正確回覆結構**：(1) 新增經濟量級段（主表之後）；(2) 新增量級與基準表；(3) 若量級小，
  寫出「精確估計的小效果」的價值，不迴避。
- **句式**：
  > "We now report that a one-standard-deviation increase in [X] corresponds to a [p]% change in [Y]
  > relative to the sample mean ([m]% of a standard deviation), and we benchmark this against
  > [Author, Year]'s estimate for [setting] (new Table 5, p. 21). The magnitude is [smaller than]
  > the U.S. benchmark, which we interpret in light of [institutional reason] (p. 22, ll. 8–15)."

### 回覆信語氣的台灣常見樣態（會被讀成不專業）

| 常見寫法 | 問題 | 改法 |
|---|---|---|
| 每一點都以 "We sincerely apologize" 開頭 | 過度道歉讀成沒有立場；道歉只用於自己寫不清楚的地方 | 感謝具體、道歉限一次 |
| "We have revised according to the reviewer's opinion." | 沒說改了什麼；"opinion" 貶低了意見 | "We have [specific change] (p. X)." |
| "We have added the literature suggested by the reviewer." | 只加引用不整合＝引用安撫；審稿人看得出來 | 說明該文獻如何改變論證，並引用新段落 |
| "The reviewer is right." 出現十次 | 讀成順從而非判斷 | 只在真正同意時用，其餘寫「我們同意此意見的方向」 |
| 把不同審稿人的相同意見各回一次、內容互相引用 | 審稿人看不到彼此的回覆，引用會斷鏈 | 每位審稿人的回覆自足；相同修改可複製段落 |
| "Due to space limitations, we did not…" | 篇幅單獨不成理由（第六節） | 給實質理由＋折衷 |

---

## 九、出信前的硬檢查（接 SKILL.md Step 4）

- [ ] 編輯信的每一點都在 cover note 有對應，且順序依編輯信
- [ ] 分診 xlsx 的每一列「狀態」皆為「已回覆」，無「待處理」
- [ ] 每個「已修改」後面有新文字引用或表號；頁行以最終 clean 版填
- [ ] 拒絕採納 ≤ 2 處，皆為三段式
- [ ] 矛盾意見在 cover note 中立說明，且在對兩位審稿人的回覆中各自承認對方觀點
- [ ] 回覆信中的每個數字與稿件一致（`thesis-consistency-audit`）
- [ ] 若本次 R&R 有新的期刊或編輯偏好，記入維護者本機版本的田野筆記（本機版本專用，
      公開包不含此檔；公開版使用者請自行建立個人筆記檔案）
