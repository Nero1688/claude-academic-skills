# NOTICE — 授權與出處對照 / License & Attribution Map

本 repo 為**合輯（collection）**，採**逐資料夾授權**。下表為權威對照；如與各技能資料夾內的 `LICENSE` / `ATTRIBUTION.md` 有出入，**以資料夾內檔案為準**。

| 技能 | 授權 | 原作者 / 來源 | 備註 |
|---|---|---|---|
| research-orchestrator | 作者原創（根 LICENSE） | 本專案作者 | 已去機構識別 |
| literature-matrix-builder | 作者原創 | 本專案作者 | 使用 CrossRef REST API（免金鑰公開服務）；摘要著作權屬各出版社，技能內已載明僅供個人研究閱讀、勿公開重製；撤稿查核亦走 CrossRef（filter=update-type:retraction），已用陽性／陰性對照實測；2026-09-20：判斷串接（judgment cascade）概念受 TypeSafe AI 的 Jev／System One 公開發表啟發；未使用其 API、未借程式碼；`screen_cascade.py` 預設不出站 |
| bilingual-paper-reader | 作者原創 | 本專案作者 | 零第三方相依；高亮持久化以瀏覽器原生 Selection/Range API 自行實作，未內嵌任何 JS 函式庫 |
| phd-researcher | **混合**：階段 1–3 原創；階段 4 模組 **CC BY-NC 4.0** | 階段 4：Cheng-I Wu (Imbad0202) / `academic-research-skills` | 🔒 非商業；保留資料夾內 `ATTRIBUTION.md`；原技能名已更名去識別 |
| tej-data-scout | 作者原創（方法論） | 本專案作者 | 已移除 catalog 的 TEJ Pro 訂閱介面完整導航樹與其來源標示；改為導覽方向＋官方公開連結；加入資料庫中立與方法建議 |
| tej-variable-mapper | 作者原創 | 本專案作者 | — |
| tej-data-wrangler | 作者原創 | 本專案作者 | — |
| r-spss-syntax-architect | 作者原創 | 本專案作者 | — |
| ob-hrm-scale-adaptor | 作者原創 | 本專案作者 | 已改寫為合規版：不重製受著作權保護之完整量表題項 |
| qualitative-thematic-coder | 作者原創 | 本專案作者 | — |
| academic-journal-polisher | 作者原創 | 本專案作者 | 2026-09-20 概念借鑑：Nanako0129/sepia（MIT），同上（中文稿版） |
| q1-journal-polisher | 作者原創 | 本專案作者 | 2026-09-20 概念借鑑：Nanako0129/sepia（MIT）三層去 AI 協議與句長離散度訊號；`prose_metrics.py` 自撰、無其文字或語料；目的為審稿人可讀性，非規避偵測 |
| q1-journal-reviewer | 作者原創 | 本專案作者 | — |
| citation-verifier | 作者原創 | 本專案作者 | — |
| phd-milestone-tracker | 作者原創 | 本專案作者 | 規則為**範例模板**；已去機構識別，具體數字請使用者替換 |
| qual-exam-coach | 作者原創 | 本專案作者 | 同上，考科可調整 |
| management-figure | **MIT** | Yuan Yizhe (Yuan1z0825) / `nature-skills` | 保留資料夾內 `ATTRIBUTION.md` 與 MIT 聲明；2026-09-20 追加：diagram-design（MIT）視覺紀律、frontend-design（Apache-2.0）概念；`event_study_plot()` 自撰 |
| academic-slides | **MIT** | Zara Zhang (© 2025) | 保留資料夾內原 `LICENSE`；**勿更換版權人姓名** |
| academic-pptx | **MIT** | 原技能作者（README 標示 MIT） | 保留 SKILL 與 MIT 聲明；**為授權審慎已移除原附的 PDF**（不影響功能）；2026-09-20 概念借鑑（無程式碼）：bobyu89/codex-ppt-style-expanded「SlideWeave」（MIT，風格目錄與引導選風格流程）、hugohe3/ppt-master（MIT，範本萃取／原生編輯／原生圖表／OMML 四項工作流概念）、anthropics/skills frontend-design（Apache-2.0，先定調再產出）；見資料夾 `ATTRIBUTION.md` |
| thesis-consistency-audit | **CC BY-NC-SA 4.0** | 框架理念改作自 qqfly1to19 / `awesome_proofreading_auto` | 🔒 非商業 + 相同方式分享（ShareAlike，整支維持 CC BY-NC-SA）；2026-09-20 追加：jamditis/claude-skills-journalism（MIT）「引用網頁須留存檔連結」概念 |
| └ anonymize_office.py | 作者原創 | 本專案作者 | 雙盲投稿的 Office 檔案身分資訊稽核與清除；純標準庫 zipfile/re，無第三方相依 |
| academic-deck-animator | 作者原創（根 LICENSE） | 本專案作者 | 融合式原創，程式全自撰；概念來源見資料夾內 `ATTRIBUTION.md`（lewislulu/html-ppt-skill MIT、hugohe3/ppt-master 等，僅借鑑方法概念，未搬程式碼）；2026-09-20 追加：1weiho/open-slide（MIT）「留言→批次套用」修改迴圈概念，未借 React 程式碼 |
| academic-poster | 作者原創（根 LICENSE） | 本專案作者 | 2026-09-20 概念借鑑：SlideWeave（MIT）風格目錄、frontend-design（Apache-2.0）先定調；Better Poster 理念（Mike Morrison）；程式 `poster_scaffold.py` 自撰 |
| defense-qa-coach | 作者原創（根 LICENSE） | 本專案作者 | — |
| nstc-grant-writer | 作者原創（根 LICENSE） | 本專案作者 | 行政規則（頁數/經費科目）以當年度公告為準，本技能不編造 |
| response-letter-craftsman | 作者原創（根 LICENSE） | 本專案作者 | — |
| research-method-selector | 作者原創（根 LICENSE） | 本專案作者 | 方法論適配框架引用 Edmondson & McManus (2007) 之公開學術文獻（概念引用，非程式碼） |
| survey-research-architect | 作者原創（根 LICENSE） | 本專案作者 | CMV 攻防依 Podsakoff 系列公開文獻 |
| interview-method-designer | 作者原創（根 LICENSE） | 本專案作者 | — |
| experiment-design-architect | 作者原創（根 LICENSE） | 本專案作者 | 情境實驗準則依 Aguinis & Bradley (2014) 公開文獻 |
| causal-inference-architect | 作者原創（根 LICENSE） | 本專案作者 | 估計量文獻(Callaway & Sant'Anna 等)為公開學術引用,非程式碼 |
| text-analytics-architect | 作者原創（根 LICENSE） | 本專案作者 | LLM 標註紀律為方法論指引;使用者需自行遵循各平台語料條款；2026-09-20 概念借鑑：anthropics/financial-services（Apache-2.0）10-K／法說會分析構念，對映到台灣年報；未借程式碼 |
| public-disclosure-scout | 作者原創（根 LICENSE） | 本專案作者 | 僅路由至官方免費公開揭露源;抓取需自行遵循各站台服務條款與政府開放資料授權。動態抓取升級階梯之「網頁轉 LLM 可讀結構」概念借鑑 unclecode/crawl4ai（Apache 2.0），僅取概念未取依賴，並明訂禁用其 stealth 反偵測功能；2026-09-20 概念借鑑：jamditis/claude-skills-journalism（MIT）頁面監測與引用存檔模式；`archive_url.py` 自撰、僅連 archive.org；未採用其付費牆相關子技能 |
| multi-source-data-integrator | 作者原創（根 LICENSE） | 本專案作者 | 資料整合方法論指引;實體解析/調解概念為通用資料工程與計量方法 |
| reproducibility-architect | 作者原創（根 LICENSE） | 本專案作者 | 可重現性方法論指引;引用 renv/conda/Zenodo 等開源工具與頂刊資料編輯規範(概念引用)；2026-09-20 概念借鑑：posit-dev/skills（MIT）Quarto 可重現報告與 R Markdown 遷移指引，僅指向其 repo 為權威來源 |
| global-opendata-scout | 作者原創（根 LICENSE） | 本專案作者 | 僅路由至國際組織公開端點（World Bank／Eurostat／ILOSTAT／IMF／UN Data），皆為免金鑰公開服務；各源之資料授權與再散布條件以其官方公告為準。⚠️ UN Data 端點僅提供 HTTP（明文），詳見技能內警告；2026-09-20：public-apis/public-apis（MIT）與 unclecode/crawl4ai（Apache-2.0）僅作參考連結（REFERENCE-ONLY，未借用）；`_gov_tls.py` 自撰、自本版起隨本技能公開 |
| journal-submission-scout | 作者原創（根 LICENSE） | 本專案作者 | 掠奪性期刊篩查框架採用 Think.Check.Submit（公開倡議，概念引用）；指標取自 OpenAlex／DOAJ／Crossref 免金鑰公開 API。**不提供 JIF、接受率、ABS／FT50／SCImago 分級**——該等為專有資料，本技能不重製亦不臆測 |
| research-framework-figure | 作者原創（根 LICENSE） | 本專案作者 | 程式全自撰（SVG 直出、PPTX 走 DrawingML）；附之範例 JSON 為**匿名通用模板**，不含任何真實研究設計；2026-09-20 概念借鑑：cathrynlavery/diagram-design（MIT）視覺紀律、frontend-design（Apache-2.0）先定調；新版式 sample_flow（PRISMA 2020／樣本刪減）與 `count_elements.py` 自撰 |
| spatial-data-architect | 作者原創（根 LICENSE） | 本專案作者 | 依賴 h3（Apache 2.0）與 pandas（BSD-3），皆為使用者自行安裝之第三方套件，本包未內含其程式碼；座標系轉換與空間自相關為通用方法學 |

## 未收錄（但推薦）
| 工具 | 狀態 | 說明 |
|---|---|---|
| check-citations | **未收錄本 repo** | 上游 `PHY041/claude-skill-citation-checker` **未附授權檔＝保留一切權利**，不可重製。請至原 repo 自行 clone 使用，與本包 `citation-verifier` 搭配。 |

## 圖例
- **作者原創** = 採根目錄 [`LICENSE`](LICENSE)（MIT，僅涵蓋原創部分）
- **MIT** = 保留原作者 MIT 授權與姓名標示
- **🔒 CC BY-NC / BY-NC-SA** = 含非商業條款，僅供非商業學術用途

## 授權共存與匿名說明
本 repo 為「合輯」：CC BY-NC-SA 的 ShareAlike 僅拘束 `thesis-consistency-audit` 該資料夾本身，不傳染其他技能。為建立與特定機構之間的防火牆，機構名稱與學校特定規則已去識別／改為範例模板；具體修業規定請以使用者所屬系所正式公告為準。
