# 來源標示 (Attribution)

本技能的 Step 0 引導流程、`references/academic-style-catalog.md` 的六種學術場合
風格目錄、以及 `references/native-pptx-workflows.md` 的四個原生 PPTX 工作流文件，
概念養分來自下列三個來源。所有文字與程式碼均為本技能自行撰寫，未直接複製任何
外部 repo 的程式碼。

## 借用的設計模式（非程式碼）

### SlideWeave（bobyu89/codex-ppt-style-expanded）— 先問受眾/時長/場合、風格目錄與比較式收斂

來源：[bobyu89/codex-ppt-style-expanded](https://github.com/bobyu89/codex-ppt-style-expanded)
（展示名稱「SlideWeave｜圖敘簡報」；Skill 呼叫名稱為 `$codex-ppt-style-expanded`，
repo 名稱本身不含 "slideweave" 字樣）。授權：MIT License，
Copyright (c) 2026 codex-ppt-style-expanded contributors。

查證方式（2026-09-20，直接查證，非轉引）：以 GitHub API 讀取
`repos/bobyu89/codex-ppt-style-expanded`（確認存在、MIT、89 stars、最後 push
2026-09-11）與其 `LICENSE`（確認版權字串），並直接取得
`raw.githubusercontent.com/bobyu89/codex-ppt-style-expanded/main/README.md`
逐字讀過。

**借用了什麼**（兩個具體概念，非程式碼）：

1. **先問受眾/用途/時長/機構背景再動手，且已有答案不重問**——該專案 README
   「從內容到簡報」流程表第一階段「了解需求」明列：「用途、聽眾、時間、素材，
   以及學校／公司／實驗室背景；已有答案不重問」。本技能的 Step 0 三題引導
   （5 秒訊息／場合與時長／投影機可讀性）與
   `academic-style-catalog.md` 的「三題引導→候選比較→收斂」流程，承接的正是
   這個「先問情境參數、答過不重問」的設計精神，改寫為學術簡報六種場合適用的版本。
2. **給少數候選並排比較，而非一次定案**——該專案 README 同一流程表「看圖選
   風格」階段明列：「預設比較三種、每輪最多五種」；其風格目錄以四大分類
   （手繪擴充 9 種、幾何與強烈視覺 4 種、原始風格 11 種、延伸風格 12 種，
   合計 36 種）供指定與比較。本技能的
   `academic-style-catalog.md` 借用「維護一份場合風格目錄、每次收斂到
   ≤3 個候選再定案」的概念，改寫為六種**學術場合**（journal-editorial、
   thesis-defense、seminar-45min、conference-15min、teaching、
   poster-session-talk）而非該專案的視覺美術風格（如包浩斯、孟菲斯、水墨人文等）。

**未借用什麼**：
- **未借用程式碼**。該專案是完整的 Codex/Claude skill 套件（含 AI 生圖、
  draw.io 流程圖產生、簡報渲染管線等實作），本技能僅借用其 README 明文記載的
  「先問情境、給候選比較」兩個流程概念，未閱讀或移植其 skill 內部程式邏輯。
- **未借用其 36 種視覺美術風格的具體樣式定義**（手繪、包浩斯、孟菲斯、
  水墨人文、麥肯錫顧問風等）——本技能的六種風格是依「場合」（審稿／口試／
  研討會／教學等）分類，與該專案依「視覺美學」分類的風格目錄是兩套不同的
  分類軸，僅共用「維護目錄＋比較式收斂」這個上層概念。
- **未借用其 AI 圖像生成、draw.io 原始檔工作流、字體搭配（手寫標題＋清楚正文）
  等技術實作**——這些是該專案針對「圖敘簡報」（插畫化簡報）的特化功能，與
  本技能鎖定的「證據優先、克制行銷語氣」學術簡報定位不同，未參考其實作方式。

查證更正紀錄：本條目研究初期曾誤以「SlideWeave」字面比對到另一個同名相近的
GitHub repo（RFYoung/slideweaver），經進一步核對其 README 內容與本次要借用的
「先問受眾/時長/場合」概念不符，判斷比對錯誤；後續以 repo 描述文字
（"SlideWeave｜圖敘簡報"）重新查證，確認正確來源為
bobyu89/codex-ppt-style-expanded，上述兩個借用概念在其 README 中均有逐字對應，
查證通過。此處記錄修正過程，是為誠實揭露方法論而非隱藏先前的比對錯誤。

### hugohe3/ppt-master — 四個原生 PPTX 工作流的概念（本 repo 家族第三次致謝）

來源：[hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，MIT License。

**這是本 repo 家族第三次借用 ppt-master 的概念，且與前兩次概念不重複**：
第一次是 `academic-deck-animator/ATTRIBUTION.md` 的「原生 PPTX 轉場與物件進場
動畫的參數化管線」；第二次是 `research-framework-figure/ATTRIBUTION.md` 的
「SVG 作為中介表示法的轉換管線」；本次（第三次）借用的是「**四個原生 PPTX
工作流的分類方式**」——範本萃取、原生編輯既有檔、原生圖表/表格、公式插入——
這是把「用原生 OOXML 物件模型做事」這件事拆成四個獨立能力範疇來描述與記錄，
與前兩次分別針對「動畫時序」與「向量圖形轉換管線」的窄用途概念是不同層次、
不同範疇的借用，不構成重複致謝。

**借用了什麼**：「原生 PPTX 能力應拆成範本萃取／原地編輯／原生圖表表格／
公式插入四個獨立工作流分別記錄其能力邊界」這個**分類與文件化方式**，改寫為
`references/native-pptx-workflows.md` 中對應本技能使用 `python-pptx` 1.0.2
的四段落結構。

**未借用什麼**：
- **未借用任何程式碼**。`scripts/pptx_template_distill.py` 與
  `scripts/test_pptx_template_distill.py` 均為本技能自行撰寫，讀取 theme XML
  與合成測試檔的實作方式獨立設計，未參考 ppt-master 的原始碼。
- **未借用其技術選型**（ppt-master 借用 SVG 中介表示法達成向量圖形轉換，
  本技能的範本萃取直接用 `zipfile`＋`xml.etree.ElementTree` 讀 theme part，
  兩者技術路徑不同，僅上層的「四個工作流」分類概念相通）。

### frontend-design — 先定調再產出的流程概念

授權：Apache License 2.0。比照本 repo 家族既有慣例（見
`research-framework-figure/ATTRIBUTION.md`、`management-figure/ATTRIBUTION.md`
的 frontend-design 段落），本技能不為其編造特定 GitHub repo 網址，僅援引其
「先確立目的與情境、再動手產出」的流程精神。

**借用了什麼**：產出簡報前先確立受眾／場合／時長等情境參數，再收斂到風格與
內容的**流程順序概念**，具體化為本技能 Step 0 的三個問題與
`academic-style-catalog.md` 的三題引導流程。

**未借用什麼**：**未借用程式碼**。本技能未使用 `frontend-design` 的任何實作
或範本，僅借用其「先定調再產出」的流程順序，與 SlideWeave 條目所借用的
「先問情境參數」概念在方向上一致但來源獨立——兩者並非重複記帳：frontend-design
提供的是「為何要先定調」的一般性流程哲學，SlideWeave 提供的是「具體要問哪些
情境參數、且答過不重問、比較幾個候選」的操作細節，本技能的 Step 0 與風格目錄
是兩者的合成，而非其中一方的重複引用。

## 相依套件

| 套件 | 授權 | 用途 |
|---|---|---|
| `python-pptx` | MIT | 已是本技能家族既有相依（1.0.2）；`scripts/pptx_template_distill.py` 使用其公開物件模型讀取投影片尺寸與版面配置，theme 色彩/字型則另行以標準庫 `zipfile`＋`xml.etree.ElementTree` 直接解析，未新增任何 pip 套件 |

本技能供學術研究使用。
