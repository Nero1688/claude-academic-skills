# 來源標示 (Attribution)

本技能為原創作品;所有內容自行撰寫,未複製任何外部 repo 的程式碼。

## 概念來源

- **KingsleyOWO/Semark**(https://github.com/KingsleyOWO/Semark,Apache 2.0)
  `references/document-preprocessing.md`(複雜揭露文件的前處理)借鑑 Semark 的核心概念:
  **用版面感知分析 + OCR 把複雜文件轉成保留語意結構的 markdown**(表格還原、多欄依序、
  source map、PII 遮罩),供下游 LLM/文字分析使用。本技能僅汲取此**方法概念**寫成
  文件指引,**未採用其程式碼、Docker 服務或依賴**(Semark 鏈上的 PyMuPDF/MuPDF 為
  AGPL-3.0,故刻意不引入程式碼,只在自行產出乾淨文字的層次借鑑其思路)。
  感謝作者以 Apache 2.0 開源這套「語意化文件處理」的思考。

- 本技能的方法紀律(LLM 標註信效度、中文 CKIP/jieba 斷詞、方法階梯)為原創,
  引用之學術方法(Podsakoff、BERTopic 等)為公開文獻概念引用,非程式碼。

- **anthropics/financial-services**
  (https://github.com/anthropics/financial-services,Apache-2.0,
  2026-09-20 實抓 LICENSE:`/blob/main/LICENSE`)
  `references/disclosure-constructs-map.md`(美國分析師構念 ↔ 台灣揭露文件對照表)
  借鏡該專案分析師端 10-K／法說會分析的構念拆解方式(如 MD&A、prepared remarks
  vs Q&A 的結構性區分)。本技能僅汲取此**分析構念概念**重新撰寫為對照表與台灣
  情境對策,**未複製其任何程式碼**,亦未採用其任何金融分析管線或提示詞範本。
