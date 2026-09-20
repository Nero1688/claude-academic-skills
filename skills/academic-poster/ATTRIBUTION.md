# 來源標示 (Attribution)

## 借用的設計模式(非程式碼)

### SlideWeave(codex-ppt-style-expanded)— 先問情境、看樣張比較再定案的流程

專案:[bobyu89/codex-ppt-style-expanded](https://github.com/bobyu89/codex-ppt-style-expanded)
(展示名稱「SlideWeave｜圖敘簡報」,Skill 呼叫名稱為 `$codex-ppt-style-expanded`)。
授權:MIT License,Copyright (c) 2026 codex-ppt-style-expanded contributors。
查證日期:2026-09-20,以 GitHub API 實抓 repo metadata、LICENSE 全文、README
全文核對(非僅憑名稱比對)。

**借用了什麼**(流程精神,非程式碼):
1. **先問情境再產出**——其 README「了解需求」階段列出「用途、聽眾、時間、素材,
   以及學校／公司／實驗室背景」,已有答案不重問。本技能 Step 1「情境與規格
   (一次問完)」的四項提問(規模/素材/版式哲學/語言與識別)呼應同一精神。
2. **看實際樣張比較、非憑空描述再選定風格**——其「看圖選風格」階段預設比較三種
   (每輪最多五種),讓使用者看縮圖差異後才決定。本技能 Step 1 第3項「版式哲學
   二選一(給使用者看差異再選)」——三欄式 vs. Better Poster 式先講清楚差異再選——
   即同一設計邏輯的海報版收斂。

**未借用什麼**:
- **未借用任何程式碼**。`scripts/poster_scaffold.py` 為本技能自行撰寫的
  python-pptx 腳本,與該專案的實作(AI 圖像背景生成、draw.io 流程圖整合)無關。
- **未借用其 36 種內建繪圖風格目錄**(手繪、粉筆板書、剪紙拼貼等)——本技能的
  版式選擇軸是「傳統三欄式 vs. Better Poster 式」這種資訊密度/版面哲學的二分,
  與該專案「視覺美術風格」的分類維度不同,不適用也未移植。
- **未借用其 AI 圖像生成流程**——本技能的圖表一律交棒給 `management-figure`
  產生統計圖,或由使用者提供現成圖檔;`poster_scaffold.py` 找不到圖檔時只畫
  明確標示的佔位框,不生成替代圖像。

### frontend-design — 先定調再產出的流程概念

沿用本技能家族既有慣例(見 `research-framework-figure/ATTRIBUTION.md`、
`management-figure/ATTRIBUTION.md`),本技能家族一貫將 `frontend-design` 當作
一項「技能」引用,而非特定 GitHub repo。授權:Apache License 2.0。

**借用了什麼**:產出前先確立目的與情境(讀者要在多短時間內看懂什麼、產出物要
用在哪個場合)的流程概念。本技能 Step 1「情境與規格(一次問完)」——先問研討會
規定、素材、版式哲學、語言識別,再動手產出——即此精神在海報情境的落地。

**未借用什麼**:未借用任何程式碼或範本;`poster_scaffold.py` 與
`templates/poster-spec.json` 均為本技能自行設計。

### Better Poster(Mike Morrison)— 主發現放大、資訊密度精簡的理念

理念引用,非程式碼、非特定 repo。SKILL.md 本文 Step 1 已註明理念來源
(「Better Poster 式……理念source:Mike Morrison Better Poster 運動」)。

**借用了什麼**:「中央大字放主發現一句話,兩側資訊精簡」的版式哲學,以及
「資訊密度是海報的敵人,主發現要能在遠距離、短時間內被看懂」的核心主張。
`poster_scaffold.py` 的 `better-poster` 版式(中央區放大 key_finding 至
≥86pt、左右側欄縮小為支撐資訊)即此理念的具體排版實作。

**未借用什麼**:未借用程式碼(Mike Morrison 的原始主張以演講與部落格文章形式
流通,並非軟體專案);未直接複製其海報範本的圖像或版型檔案。

## 座標配置的推算說明

`references/poster-layout.md` 對兩種版式僅有 ASCII 示意圖與「欄間距 ≥2cm」等
局部規則,未給出可直接寫入程式的精確座標。`scripts/poster_scaffold.py` 中
`build_blocks_three_column()` 與 `build_blocks_better_poster()` 的具體區塊
座標(以整頁比例表示,如標題帶高 7.5%、頁邊距 2–3% 等)為本技能依該文件版面
骨架精神自行推算,非抄自任何外部專案,亦非該文件明文規定的數字——調整時應
回頭核對是否仍符合 `poster-layout.md` 的欄間距/頁邊距/縮圖自檢等原則。

## 查證紀錄

SlideWeave 來源在查證過程中曾發生一次誤配:最初以 GitHub 名稱字面搜尋比對到
`RFYoung/slideweaver`(星數少、內容為 python-pptx 圖形庫/QA 檢查,與海報或三層
閱讀動線設計無關);複核後(2026-09-20,GitHub API 核對 repo 描述/LICENSE/
README)確認正確來源即上表所列的 `bobyu89/codex-ppt-style-expanded`。過程記錄
於維護者的 LESSONS 踩坑紀錄 L-031（不隨本包發布）。

## 相依套件

| 套件 | 授權 | 用途 |
|---|---|---|
| `python-pptx` | MIT | 產生/讀回驗證 .pptx,以 pip 正常安裝使用,未修改其原始碼 |

本技能供學術研究使用。
