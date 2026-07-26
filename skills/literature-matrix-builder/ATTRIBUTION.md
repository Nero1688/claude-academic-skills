# 來源標示 (Attribution)

## 借用的程式碼

**無。** 本技能的 `scripts/litmatrix.py` 為自行撰寫，未複製任何外部專案的程式碼。

建置前曾盤點 GitHub 上的相關方案（如 `habanero` CrossRef client、GROBID、
`pybliometrics`、社群的 paper-writer-skill 等），最終判斷：
- `habanero` 雖為 MIT 且可直接使用，但本技能只需要「以 DOI 取單筆 metadata」
  這一個功能，直接用 `requests` 呼叫 CrossRef REST API 即可，
  多一層相依反而增加使用者的安裝負擔。
- GROBID 功能最強，但需獨立跑 Java/Docker 服務，不符「輕量自包含」的設計目標。

**因此本技能未借用他人程式碼，也不宣稱受其設計啟發**——未實際閱讀其原始碼。

## 使用的資料服務

**CrossRef REST API** — https://api.crossref.org/
- 免金鑰、免費，提供 DOI 對應的書目 metadata。
- 依其 polite pool 慣例，建議在 User-Agent 帶聯絡信箱；本技能以環境變數
  `CROSSREF_MAILTO` 提供，不硬編碼。
- ⚠️ CrossRef metadata 多為開放，但**摘要（abstract）著作權通常仍屬各出版社**，
  僅供個人研究閱讀，勿公開重製散布。

學術著作若大量仰賴 CrossRef 取得書目，慣例上可於方法或致謝節說明資料來源。

## 相依套件（以 pip 正常安裝使用，未修改其原始碼）

| 套件 | 授權 | 用途 |
|---|---|---|
| `requests` | Apache-2.0 | HTTP 呼叫 CrossRef |
| `openpyxl` | MIT | 產出 Excel 矩陣 |
| `pypdf` | BSD-3-Clause | 從 PDF 抽取 DOI |

本技能供學術研究使用。
