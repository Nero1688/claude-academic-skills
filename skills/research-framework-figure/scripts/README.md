# scripts — 研究架構圖產生器

## framework_figure.py

從 JSON 規格產出研究架構圖。**SVG 輸出零依賴**（只用標準庫），
PPTX 輸出才需要 `python-pptx`。

### 安裝

```bash
pip install python-pptx
```
（只有要出 PPTX 才需要；出 SVG 不必裝任何東西。）

### 用法

```bash
python framework_figure.py spec.json -o fig.svg
python framework_figure.py spec.json -o fig.pptx --format pptx
python framework_figure.py --demo -o demo.svg
python framework_figure.py --list-templates
```

| 參數 | 說明 |
|---|---|
| `spec` | JSON 規格檔路徑，格式見 `../references/framework-figure-spec.md` |
| `-o, --output` | 輸出路徑（副檔名決定格式，或用 `--format` 指定） |
| `--format` | `svg`（預設）或 `pptx` |
| `--demo` | 用內建示範規格產圖，不需要規格檔 |
| `--list-templates` | 列出可用版式 |

### 版式

| template | 說明 |
|---|---|
| `mediation_dual_controls` | 中介＋雙控制變數框（台灣商管論文最常見） |
| `mediation` | 簡單中介 X→M→Y |
| `moderation` | 調節模型（箭頭指向路徑中點） |
| `moderated_mediation` | 被調節的中介 |
| `serial_mediation` | 序列中介 X→M1→M2→Y |

### 檢視產出

SVG 可直接用瀏覽器開啟。若要在本機預覽，把 SVG 包進一個 HTML：

```bash
{ echo '<!doctype html><meta charset="utf-8"><body>'; cat fig.svg; echo '</body>'; } > preview.html
```

### 字型行為（重要）

SVG 的 `font-family` 寫成 `Times New Roman, DFKai-SB, BiauKai, serif`——
**西文字型排在前面**，瀏覽器對每個字元逐一 fallback：英數用 Times New Roman，
中文因 Times New Roman 無該字元而 fallback 到標楷體（DFKai-SB）。
這是 SVG 實現中英混排字型規範的正確作法。

⚠️ 若檢視端沒有安裝標楷體，中文會再 fallback 到系統預設字型。
**產出後請在有標楷體的機器上確認一次**，不要假設已套用成功。

PPTX 輸出則透過 `a:ea` XML 元素明確指定東亞字型為標楷體
（python-pptx 的 `font.name` 只會設定西文字型，中文必須另外寫 `a:ea`）。

### 輸出到 Word

SVG 可直接拖曳插入 Word（2016 以上原生支援向量 SVG，縮放不失真）。
若期刊要求 300dpi 點陣圖，用 Inkscape／Illustrator 匯出，或在 PowerPoint
中「另存為圖片」選 300dpi——不要用螢幕截圖。
