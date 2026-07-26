# scripts — 雙欄論文閱讀器

## 檔案

| 檔案 | 說明 |
|---|---|
| `pdf_to_paper.py` | PDF／純文字 → 論文資料檔（JSON） |
| `reader.html` | **可重複使用**的雙欄閱讀器，零依賴、離線可用 |
| `sample_paper.json` | 範例資料檔，可直接拖進 reader.html 看效果 |

## 安裝

```bash
pip install pypdf
```
只有 `pdf_to_paper.py` 讀 PDF 時需要；`reader.html` 不需要任何東西。

## 用法

```bash
python pdf_to_paper.py paper.pdf -o paper.json --title "論文標題"
python pdf_to_paper.py ocr.txt   -o paper.json --format txt
python pdf_to_paper.py paper.pdf -o paper.json --min-chars 150
```

| 參數 | 說明 |
|---|---|
| `--format` | `pdf`（預設依副檔名）或 `txt` |
| `--min-chars` | 段落最短字元數，低於此值視為雜訊丟棄（預設 100） |
| `--title` | 手動指定標題（**建議加**，自動猜測常抓到版權聲明） |

產出 JSON 後，由 Claude 填入 `glossary`（術語對照）、每段的 `trans`（譯文）
與 `marks`（預先標記），然後：

1. 用瀏覽器開啟 `reader.html`
2. 把 JSON 拖進去（或按「開啟論文 JSON」）

## 閱讀器操作

| 動作 | 方式 |
|---|---|
| 載入論文 | 拖放 JSON，或按「開啟論文 JSON」 |
| 畫螢光筆 | 選取文字 → 浮出工具列 → 選類別 |
| 清除某段標記 | 選取該範圍 → 按「清除」 |
| 匯出筆記 | 按「匯出筆記 (Markdown)」，依五類分組並含術語表 |
| 清空本篇標記 | 按「清除本篇標記」（會再確認一次） |

五色分類：**核心論點**（黃）、**創新點／貢獻**（綠）、**方法／資料**（藍）、
**限制／缺口**（紅）、**可引用金句**（紫）。判準見 `../references/highlight-taxonomy.md`。

## 技術說明

**高亮持久化**用瀏覽器原生 Selection / Range API，以
`{段落索引, 欄位, 字元起訖, 類別}` 序列化存進 `localStorage`（鍵為 `bpr:<論文id>`）。
因為段落 DOM 由本程式自己產生、結構受控，不需要 Rangy 這類處理任意 DOM 的函式庫
（詳見 `../ATTRIBUTION.md`）。**零第三方相依，完全離線可用。**

論文 `id` 由前五段內容的 SHA-256 前 16 碼決定，因此同一篇論文重新轉檔仍會沿用既有標記。

## 已知限制

- ⚠️ **標記存在 localStorage**：清除瀏覽器資料、換瀏覽器、換電腦都會不見。
  重要筆記請用「匯出筆記」存成 Markdown 備份。
- **掃描版 PDF（無文字層）抽不到文字**，工具會明確報錯。請先用
  `ocrmypdf` 或 Adobe Acrobat 做 OCR，或改用 `--format txt` 餵已 OCR 的純文字。
- **表格會被壓平成亂序文字**——這是 PDF 文字抽取的先天限制。工具會用
  `skip: likely_table` 標出疑似表格的段落，翻譯時略過即可。
- **兩欄公式與多欄排版**可能造成切段錯亂，此時調整 `--min-chars` 或手動修 JSON。
- **翻譯需要 Claude 在場**：閱讀器是靜態 HTML，沒有 LLM，無法自己翻譯。
