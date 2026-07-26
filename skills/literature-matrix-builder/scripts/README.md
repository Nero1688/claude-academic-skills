# scripts — 文獻矩陣建置工具

## litmatrix.py

### 安裝

```bash
pip install requests openpyxl pypdf
```

| 套件 | 何時需要 |
|---|---|
| `requests` | **必要**——CrossRef 查詢 |
| `openpyxl` | 產 Excel 時必要 |
| `pypdf` | 從 PDF 自動找 DOI 時必要（改用 `--doi` 手動指定就不需要） |

### 子指令

```bash
python litmatrix.py init   -d ./lit                       # 建資料夾結構
python litmatrix.py add    -d ./lit --pdf 01_pdf/x.pdf    # 自動找 DOI 後加入
python litmatrix.py add    -d ./lit --doi 10.1177/...     # 直接用 DOI 加入
python litmatrix.py lookup --doi 10.1177/...              # 只查不寫入（驗證用）
python litmatrix.py list   -d ./lit                       # 看填寫進度
python litmatrix.py build  -d ./lit                       # 產出 Excel
```

### 資料夾結構

```
lit/
  01_pdf/        PDF 原檔
  02_notes/      每篇的閱讀筆記（Markdown，自行建立）
  03_output/     產出的 literature_matrix.xlsx
  library.json   文獻庫（單一事實來源，可直接編輯填綜整欄）
```

**填綜整欄有兩種方式**：直接編輯 `library.json`（10 個欄位在每筆條目裡），
或在產出的 Excel 黃底欄填完後自行回填 JSON。建議以 `library.json` 為準，
Excel 視為產出物而非編輯介面（避免兩邊不同步）。

### CrossRef 禮貌池

CrossRef 建議在 User-Agent 帶聯絡信箱以取得較穩定的服務品質（polite pool）。
設環境變數即可，**腳本不硬編碼任何信箱**：

```bash
export CROSSREF_MAILTO=you@example.com
```

不設也能用，只是走一般池。

### Excel 產出

兩張工作表：

1. **文獻矩陣** — 20 欄。前 7 欄書目（自動）、中間 10 欄綜整（黃底＝待填）、
   末 3 欄摘要與檔案資訊。已設凍結窗格（C2）與自動篩選。
2. **待補清單** — 列出哪幾篇還缺哪些綜整欄，開會或趕進度時直接看這張。

### 已知限制

- **掃描版 PDF 抽不到 DOI**（無文字層），需先 OCR 或改用 `--doi`。
- **CrossRef 未必有摘要**——許多出版社不釋出，空白是常態而非錯誤。
- **APA7 只保證期刊論文格式正確**；書籍／章節／會議論文會標
  「[需人工確認格式]」，請依 APA7 手冊調整。
- CrossRef 查無 DOI 時**直接報錯不補資料**，這是刻意設計（防幻覺文獻）。
