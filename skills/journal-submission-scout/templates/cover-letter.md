# 投稿信模板（中英雙版，含揭露聲明與推薦審稿人區塊）

本模板接在 SKILL.md Step 5「輸出投稿策略」之後：候選期刊定了，投稿信才有對象。
投稿信是編輯桌面審查那 10 分鐘的一部分（見 `q1-journal-reviewer` 的
`references/desk-reject-checklist.md` 第一節第 8 站），不是摘要的複製——它回答三個
編輯真正在問的問題：**你的貢獻是什麼、為什麼投我們、有沒有合規問題**。

使用紀律：
- 一頁內。每個〔〕都要填；填不出「貢獻一句話」或「與本刊近三年對話的文獻」，代表稿件
  本身還沒準備好，回 `q1-journal-reviewer`。
- 投稿信的形式（必要與否、是否改為投稿系統的結構化欄位、要不要列推薦審稿人）
  **以該刊當期作者指南為準**；本模板只給內容骨架。
- 與該刊近三年對話的文獻**必須真實、必須已在稿件參考文獻中被實質引用**。用
  `python scripts/journal_scout.py search` 或直接讀該刊目次確認；本 skill 不替使用者
  生成任何「該刊近年發表了…」的陳述，寫錯一篇就是編輯眼中的紅旗。
- 禁止出現 impact factor、JIF、接受率、期刊排名等字樣——編輯知道自己期刊的指標，
  寫出來只顯示投稿者在意的是指標而非讀者；本 skill 本來就不提供這些數字。
- 推薦與迴避審稿人依 `references/reviewer-suggestion-ethics.md`；本模板只留欄位。

---

## 一、六段結構（兩個語言版本共用）

| 段 | 內容 | 一句話上限 |
|---|---|---|
| 1 | 稿件標題、投稿類別（一般論文／研究短文／特刊）、字數 | 2 句 |
| 2 | **貢獻一句話**：既有觀點 A → 本文證據 B → 因此 C 需要修正；含一個量級數字 | 1–2 句 |
| 3 | **為什麼是這本**：守備範圍吻合＋與本刊近三年 2–3 篇文獻的實質對話（延伸／挑戰／補足） | 3–4 句 |
| 4 | **識別優勢一句**：設計、變異來源、平行趨勢敏感度的頭條數字 | 1–2 句 |
| 5 | **揭露區塊**：原創性與不重複投稿、利益衝突、資金、資料可用性、倫理審查（若適用）、AI 使用、作者貢獻、先前發表（研討會／工作論文） | 逐項一行 |
| 6 | 推薦／迴避審稿人（若期刊要求）、通訊作者聯絡方式 | 依指南 |

---

## 二、英文版（投國際期刊用）

```
[Date]

Dear Professor [Editor-in-Chief surname] and the Editorial Team of [Journal],

We are pleased to submit our manuscript entitled "[Title]" for consideration as a
[Regular Article / Research Note] in [Journal]. The manuscript is [N] words including
[references / tables / appendices — follow the journal's counting rule].

[Contribution — one sentence, with a number]
Existing work on [topic] holds that [prevailing view A]. Using [design] on [sample:
N firms, years], we show that [finding B]: a one-standard-deviation increase in [X]
is associated with a [magnitude, in % of mean or in s.d.] change in [Y], and the
effect [reverses / disappears / doubles] when [boundary condition]. This implies
that [theory T] requires [modification C].

[Why this journal — scope + dialogue]
The paper speaks directly to a conversation in [Journal]. [Author (Year), this
journal] established [claim]; [Author (Year), this journal] extended it to [setting];
our findings [qualify / extend / reconcile] this line by showing [what], which
neither study could address because [data or identification limitation].
[If applicable: The paper also responds to the call in [Author (Year), this journal]
for evidence on [question].]

[Identification advantage — one sentence]
Taiwan's [institutional feature, with legal or regulatory citation in the paper]
generates variation in [X] that is plausibly unrelated to [Y], allowing us to
separate [mechanism A] from [mechanism B]. Event-study pre-trends are jointly
insignificant, and the estimate remains bounded away from zero for violations of
parallel trends up to M̄ = [value] (Rambachan & Roth, 2023).

[Disclosures]
- Originality and exclusivity: The manuscript is original, has not been published,
  and is not under consideration elsewhere. [If applicable: An earlier version was
  presented at [conference, year] / circulated as a working paper [series, number].]
- Conflicts of interest: The authors declare no conflicts of interest. [Or specify.]
- Funding: [Funder, grant number] / This research received no external funding.
- Data availability: Firm-level data were obtained from the Taiwan Economic Journal
  (TEJ) database under an institutional license and cannot be redistributed; the
  replication package provides all code and instructions for reconstructing the
  sample from TEJ. [Adjust to the journal's data policy.]
- Ethics: Not applicable (archival data). [Or: approved by [IRB], protocol [no.].]
- Use of AI tools: [Choose one — see Section IV of this template.]
- Author contributions: [Initials — conceptualization, data, analysis, writing.]

[Reviewer suggestions — only if the journal asks]
Suggested reviewers (no conflicts of interest as defined in the journal's policy):
[Name, institution, institutional e-mail, one-line reason]. Opposed reviewer:
[Name, institution — reason stated factually, see references/reviewer-suggestion-ethics.md].

Thank you for considering our manuscript.

Sincerely,
[Corresponding author name], [position], [institution]
[Institutional e-mail], on behalf of all authors
```

---

## 三、中文版（投國內學報、TSSCI 或作為英文版起草底稿）

```
〔日期〕

〔期刊名稱〕主編暨編輯委員會 鈞鑒：

謹將拙作〈〔標題〕〉投稿貴刊，投稿類別為〔一般論文／研究短文／專題〕，
全文〔N〕字（含／不含參考文獻，依貴刊規定計算）。

〔貢獻一句話，含量級〕
既有文獻多主張〔既有觀點 A〕。本文以〔研究設計〕分析〔樣本：N 家公司、年度〕，
發現〔發現 B〕：〔X〕提高一個標準差，〔Y〕變動〔量級：占平均數 %／幾個標準差〕，
且此效果在〔邊界條件〕時〔反轉／消失／倍增〕。此結果意味〔理論 T〕需在〔C〕上修正。

〔為什麼是貴刊〕
本文延續貴刊近年關於〔主題〕的討論：〔作者（年）〕提出〔主張〕；〔作者（年）〕將之
延伸至〔情境〕。本文〔限定／延伸／調和〕此一脈絡，指出〔差異〕——這是前述研究因
〔資料或識別限制〕而無法回答的問題。

〔識別優勢〕
台灣的〔制度特徵，稿件中附法規或公告出處〕使〔X〕產生與〔Y〕無關的變異，本文據此
區分〔機制 A〕與〔機制 B〕。事件研究前期係數聯合不顯著；在平行趨勢違反達 M̄ =〔值〕
（Rambachan & Roth, 2023）之前，估計值仍顯著異於零。

〔揭露事項〕
一、本文為原創，未曾發表，亦未同時投稿其他刊物。〔如適用：初稿曾於〔研討會、年〕
    發表／曾以工作論文形式流通。〕
二、利益衝突：作者聲明無利益衝突。〔或具體說明。〕
三、經費：〔補助機關、計畫編號〕／無外部經費。
四、資料可用性：公司層級資料取自台灣經濟新報（TEJ）資料庫之機構授權，依授權條款
    不得轉散布；複製包提供全部程式碼與自 TEJ 重建樣本的步驟。〔依貴刊資料政策調整。〕
五、研究倫理：不適用（檔案資料）。〔或：經〔審查會〕核准，案號〔編號〕。〕
六、AI 工具使用：〔擇一，見本模板第四節。〕
七、作者貢獻：〔姓名縮寫——構想、資料、分析、撰寫。〕

〔推薦／迴避審稿人——僅在貴刊要求時提供〕
推薦審稿人（依貴刊利益衝突定義確認無衝突）：〔姓名、機構、機構信箱、一行理由〕。
迴避審稿人：〔姓名、機構——事實陳述理由，見 references/reviewer-suggestion-ethics.md〕。

敬請惠予審查。

〔通訊作者姓名、職稱、機構〕敬上
〔機構信箱〕（代表全體作者）
```

---

## 四、揭露聲明句庫（擇一填入，依該刊當期作者指南調整用詞）

**AI 工具使用**（多數出版商要求揭露寫作輔助、禁止列 AI 為作者、禁止用於生成或
竄改資料與分析；以該刊當期政策為準）：
- 未使用：「本研究之構想、分析與撰寫未使用生成式 AI 工具。」
  ／"No generative AI tools were used in the conception, analysis, or writing of this manuscript."
- 語言潤飾：「作者使用〔工具名稱、版本〕協助英文語句潤飾；所有內容經作者審閱並負全責，
  AI 未用於產生或分析資料。」
  ／"The authors used [tool, version] to improve the readability of the English text. All content
  was reviewed and is the sole responsibility of the authors; no AI tool was used to generate or
  analyze data."
- 程式碼輔助：「作者使用〔工具〕協助撰寫資料整理程式碼；程式碼經作者逐行驗證並收錄於複製包。」
  ／"The authors used [tool] to assist in drafting data-processing code; all code was verified
  line by line by the authors and is included in the replication package."

**資料可用性（TEJ 授權資料）**：完整寫法與複製包結構見
`anthropic-skills:reproducibility-architect`；投稿信只放一行，指向複製包。

**先前發表**：研討會發表與工作論文不構成重複發表，但要揭露；學位論文改寫的稿件，
若該刊要求揭露則以一行說明「本文改寫自第一作者之學位論文〔年〕」，不作為動機。

---

## 五、台灣商管稿件在頂刊的常見落差→具體對策（投稿信版）

編輯對三個落差的第一印象常常來自投稿信，而不是稿件。以下對照「常見寫法→改法」。

### 落差 1：情境複製——投稿信第一段就從「台灣」起手

| 常見寫法（會被讀成情境複製） | 改法（讀成理論貢獻） |
|---|---|
| "Taiwan is an emerging market characterized by high family ownership, making it an ideal setting to examine…" | 第 2 段先寫理論張力與量級；台灣在第 4 段以「識別優勢」出場，句式："Taiwan's [feature] generates variation in X that…allows us to separate A from B." |
| "This study fills the gap that no prior research has examined X in Taiwan." | 刪。缺口不是貢獻。改寫成「既有觀點 A → 本文證據 B → 理論 T 需修正 C」 |
| "Our findings provide insights for Taiwanese regulators." | 移到稿件討論節末；投稿信的貢獻句只講知識變化 |
| 第 3 段列的「本刊文獻」是與台灣有關的文章 | 列的是與**機制**有關的文章；台灣不是對話的理由，機制才是 |

### 落差 2：識別策略在投稿信裡只有一個名詞

| 常見寫法 | 改法 |
|---|---|
| "We employ a difference-in-differences design." | 一句話交代三件事：變異來源、估計量名稱、平行趨勢敏感度頭條數字（"…remains bounded away from zero up to M̄ = [value]"）。編輯看到 breakdown 值，就知道作者做過誠實區間 |
| "We use the [regulation] as an exogenous shock." | 加「誰在何時受影響、控制組是誰」半句："…which applied to firms above [threshold] from [year], leaving firms below the threshold as controls" |
| 完全不提識別（只講主題與樣本） | 第 4 段是必要段；沒有識別優勢可寫，代表定位應改為關聯研究，並在信中誠實使用 "is associated with" |

### 落差 3：貢獻句沒有數字

| 常見寫法 | 改法 |
|---|---|
| "We find that X significantly increases Y." | "A one-standard-deviation increase in X is associated with a [p]% increase in Y relative to the sample mean, comparable to [benchmark]." |
| "The results are robust to a battery of tests." | 點名一個最能回應該刊讀者疑慮的檢定："…robust to heterogeneity-robust DiD estimators and to Oster (2019) bounds." |
| "The effect is both statistically and economically significant." | 刪掉形容詞，放數字 |

### 其他台灣投稿信常見的訊號（一律刪）

- 過度謙卑的開場（"It is our great honor…"）、恭維期刊（"your prestigious journal"）。
- 承諾無條件修改（"We will revise according to any comments"）——編輯讀成沒有立場。
- 主動交代曾被其他期刊拒絕（除非該刊要求揭露先前投稿紀錄；被問到則誠實回答）。
- 列出自己的職稱、得獎、指導教授姓名當背書（雙盲期刊還會因此破功）。

---

## 六、送出前檢查

- [ ] 一頁內；六段齊全；每個〔〕已填，無殘留括號
- [ ] 貢獻句含一個量級數字，且與摘要、引言末段、結論的貢獻句一致
- [ ] 第 3 段的 2–3 篇本刊文獻：真實、在稿件參考文獻中有實質引用、與機制（非台灣）相關
- [ ] 第 4 段含變異來源、估計量名稱、breakdown 值三件事
- [ ] 揭露區塊逐項對照投稿系統必填欄位；AI 使用聲明擇一且與稿件內聲明一致
- [ ] 推薦審稿人已依 `references/reviewer-suggestion-ethics.md` 過利益衝突清單；信箱皆為機構信箱
- [ ] 全信無 impact factor／JIF／接受率／排名字樣，無恭維與過度謙卑句
- [ ] 雙盲期刊：投稿信不進審稿人視野，但稿件本身已跑 `anonymize_office.py`
