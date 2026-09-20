# 回覆信模板與措辭庫(中英對照)

## 整體結構(標準版面)

```
Response to Reviewers — Manuscript ID: XXXX
「(標題)」修訂說明

致主編的話(Cover note to the Editor)     ← 一頁內,總結主要修改
------------------------------------------
Reviewer 1
  Comment R1-1(復述)
  Response(回應+修改內容+位置)
  Comment R1-2 …
Reviewer 2
  …
附錄:主要修改對照表(意見編號|修改摘要|位置)
```

排版慣例:審查意見用斜體或灰底、回覆用正體、新增文字用引用區塊或標色說明
(「新增文字以藍色標示於修訂稿」),讓審查人一眼分層。

## 四段式範例(方法類意見,英文)

> **Comment R2-1:** *"The authors should address the potential self-selection of
> TNFD adoption. Firms with better environmental performance may be more likely
> to adopt."*
>
> **Response:** We thank the reviewer for raising this identification concern.
> We agree that selection into adoption is the first-order threat to our
> design. We now (i) report the Goodman-Bacon decomposition (Table A2: x% of
> the TWFE weight comes from forbidden comparisons, i.e., later-treated vs.
> earlier-treated units), (ii) re-estimate the main specification with the
> Callaway and Sant'Anna (2021) estimator using not-yet-treated controls
> (Table 3), (iii) show that pre-period event-study coefficients are jointly
> insignificant (Wald p = …; Figure 2) and that the estimate survives
> violations of parallel trends up to M̄ = … under Rambachan and Roth (2023)
> (Table A4), and (iv) split the sample by pre-adoption propensity to adopt
> (Table A5) so that the reviewer can see whether the effect is concentrated
> among firms most likely to self-select. The ATT of … corresponds to …% of
> the treated firms' pre-adoption mean of the outcome, which is economically
> meaningful relative to (benchmark).
>
> As a supplementary check only, Appendix C reports a Heckman two-stage
> model and a propensity-score-matched re-estimation. We state explicitly in
> the text that these address selection on observables and do not substitute
> for the design-based evidence above.
>
> **Changes:** Revised Section 5.1 "Identification" (pp. 18–22); new Table 3;
> new Figure 2; new Tables A2, A4, A5; new Appendix C; revised discussion of
> limitations (p. 31, lines 8–14).

**為什麼不能用「Heckman＋PSM＋p<.05」回自選擇**：那是家族自訂標準
（`q1-journal-reviewer/references/top-journal-standards.md` 軸 A「有但薄」欄）明列的樣態——
排除變數（產業採用密度）會透過同儕效應直接影響結果、PSM 只處理可觀測選擇、
以顯著性而非量級收尾。上面的寫法把設計面證據放正文、選擇模型降附錄並標明「僅處理可觀測選擇」，
量級句對齊 §5 落差 3；x、p、M̄、% 一律填實際數字，不得留佔位。

## 四段式範例(理論類意見,中文)

> **意見 R1-2:**「作者宣稱貢獻於訊號理論,但未說明與 Connelly et al. (2011)
> 綜述後大量後續研究的差異。」
>
> **回覆:** 感謝審查人指出理論定位不足之處。我們同意原稿對訊號理論文獻的
> 對話過於單薄。修訂稿第二章新增「訊號成本與訊號環境」一節(§2.2,頁 8–10),
> 明確定位本研究的差異:既有文獻聚焦訊號「發送者特質」,本研究則檢驗「訊號
> 環境的制度成熟度」如何改變同一訊號的定價——此為 Connelly et al. (2011)
> 指出但尚未被實證檢驗的方向。新增文字如下:「……(引用修訂稿實際段落)……」
>
> **修改位置:** §2.2(頁 8–10)新增;§6.1 理論貢獻段落改寫(頁 29,行 5–18)。

## 措辭庫

**開場感謝(具體型,擇一)**
- We thank the reviewer for this constructive suggestion, which has substantially strengthened the robustness section.
- 感謝審查人的建議,這使本文的穩健性檢驗更為完整。

**部分接受**
- We agree with the spirit of this comment. While a full ○○ analysis is not feasible given (data constraint), we have (folded-in alternative)…
- 我們認同此意見的方向。囿於(資料限制),無法完整執行○○,但已(替代做法)…

**澄清誤解(責任歸己)**
- We apologize that our original wording did not make this clear. We have rewritten the passage as follows: …
- 原稿表達未臻清楚,謹此致歉;該段已改寫為:……

**有理由不改(全信至多兩處)**
- We carefully considered this suggestion. However, because (specific reason), we believe the current specification better serves the paper's research question. We now acknowledge this alternative explicitly in the limitations section (p. X).

**回應互相矛盾的意見(在給 editor 的信中)**
- We note that Reviewer 1 suggests (A) while Reviewer 2 recommends (B). We have adopted (A) because (reason tied to research question), and we explain this choice, with due acknowledgment of the alternative, in footnote X.

## 主要修改對照表(附錄模板)

| 意見編號 | 修改摘要 | 修訂稿位置 |
|---|---|---|
| R1-1 | 主估計改 Callaway & Sant'Anna (2021)，TWFE 移附錄；Goodman-Bacon 分解（表 A2） | §5.1, pp. 18–20；表 3 |
| R1-2 | 理論定位新增 §2.2 | pp. 8–10 |
| R2-1 | 事件研究前期聯合檢定＋Rambachan-Roth 誠實區間（圖 2、表 A4）；依採用傾向分組（表 A5）；量級句 | §5.1, pp. 20–22 |
| R2-1（補充） | Heckman／PSM 降附錄，明寫僅處理可觀測選擇 | 附錄 C |

## 最後檢查清單

- [ ] 每則意見都有編號且都有回覆(零遺漏)
- [ ] 每個「已修改」都在修訂稿實際存在,頁碼行號以最終版核對
- [ ] 「不改」處 ≤ 2,且都附理由與折衷
- [ ] 語氣全文一致:專業、感謝具體、零反擊
- [ ] cover note ≤ 1 頁,主要修改 3–5 條
- [ ] 修訂稿另跑 thesis-consistency-audit(新增分析不得製造新矛盾)
