# 來源標示 (Attribution)

本技能為融合式原創作品,概念養分來自下列來源;所有程式碼均為本技能自行撰寫,
未直接複製任何外部 repo 的程式碼。

## 概念來源

1. **slides_content.json 雙引擎規格(v1.0)** — 使用者本人 2026-07 的原始設計
   (源自其與其他 AI 助手的規格討論文件)。本技能將其精煉為 v1.1:移除對外部
   repo 的 skill_id 路由依賴,改為自包含實作;欄位對照表見
   references/slides-content-schema.md 末節。

2. **hugohe3/ppt-master**(https://github.com/hugohe3/ppt-master)
   借鑑概念:原生 PPTX 轉場與物件進場動畫的參數化管線、動畫預設保守
   (「unsolicited cascade reads as the AI deck tell」)的設計哲學、
   animations 時序設定(trigger / stagger)的介面形狀。
   未複製其 SVG 產生管線與任何程式碼(該專案授權條款未明示,故僅取不受著作權
   保護的方法概念)。

3. **lewislulu/html-ppt-skill**(https://github.com/lewislulu/html-ppt-skill,MIT)
   借鑑概念:自包含 HTML 簡報+Canvas FX 分層的架構、以 CSS token 做主題、
   簡報者模式。本技能的 canvas-fx.js 為獨立重寫,只實作學術場合允許的三種
   低調特效(particle-burst / drift-field / network-lines),未搬移其 47 種
   動畫庫。

4. **maxonthegit/PPspliT**(https://github.com/maxonthegit/PPspliT)
   借鑑概念:「把動畫步驟拆成連續投影片以利轉 PDF」。該專案是 PowerPoint VBA
   增益集;本技能的 --split 模式為 Python 原生重新實作(在產生階段直接展開
   逐步頁面,而非事後拆解),實作路徑完全不同。

## 查證紀錄

原始規格文件另引用 PacktPublishing/PowerPoint-Excellence 與
giuleon/CloudPresentationPack 作為條列動畫與連線動畫來源;查證結果(2026-07-10):
前者不存在(幻覺引用),後者存在但僅為 PowerPoint 動畫素材檔非程式庫。
兩者均未採用,對應功能由本技能自行實作。
