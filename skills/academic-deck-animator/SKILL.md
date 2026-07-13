---
name: academic-deck-animator
description: 學術簡報動畫引擎:以 slides_content.json 統一規格驅動的雙引擎動態簡報產生器。引擎A html-canvas 產出自包含 HTML 簡報+Canvas 粒子特效(particle-burst、drift-field、network-lines,僅限封面/章節頁);引擎B native-pptx 產出原生 PowerPoint 檔+真正的物件進場動畫(appear/fade/wipe/fly-in,依 entry_order 與 delay_ms 排時序),另有 split 拆頁模式把逐步動畫拆成連續頁面、轉 PDF 排版不重疊。內建學術動畫克制原則(動畫服務論證,不做裝飾)。何時用:口試簡報、研討會報告、演講簡報要加動畫或動態效果、要粒子特效開場、要逐步揭示研究架構/模型/論證、要把動畫簡報轉成 PDF 講義時。觸發詞:PPT動畫、簡報動畫、動態簡報、動效、粒子特效、particle、canvas 簡報、進場動畫、飛入、淡入、逐步顯示、逐條出現、動畫拆頁、slides_content.json、簡報轉場。與 academic-pptx 劃界:那個管簡報「內容與結構」的學術決策(說什麼、怎麼編排),本 skill 管「動效實作」(怎麼動起來);先用那個定內容,再用本 skill 上動畫。與 academic-slides 劃界:那個做 Beamer 風靜態 HTML 主題與數學排版,本 skill 做動畫層與粒子特效;純靜態學術 HTML 簡報找那個。與 pptx 劃界:那個是通用 .pptx 檔案讀寫機制,本 skill 是學術動畫規格+雙引擎產生器。
---

# Academic Deck Animator(學術簡報動畫引擎)

把學術簡報從「靜態頁面」升級成「有節奏的論證」。一份 `slides_content.json` 驅動兩種輸出:

| 引擎 | 產出 | 適用場景 |
|---|---|---|
| `html-canvas` | 自包含 .html(零依賴、瀏覽器直接開) | 演講現場用自己電腦、要粒子特效與流暢網頁動效、線上分享連結 |
| `native-pptx` | 原生 .pptx(真 PowerPoint 動畫,可再編輯) | 主辦方要求交 .pptx、口試現場用別人電腦、需要委員會後修改 |

兩引擎讀同一份 JSON,可同時輸出兩種格式。

## 核心哲學:動畫是論證的節拍器,不是裝飾

學術簡報的觀眾(口試委員、審稿人、同行)對「AI 生成感」與「業配感」高度敏感。
未經設計的連環動畫是最明顯的破綻。因此本 skill 的預設值全部保守:

- 動畫唯一的正當理由:**控制資訊揭示的節奏,讓聽眾的注意力跟上論證**。
- 粒子特效只允許出現在封面、章節分隔頁、結尾頁——內容頁一律禁用。
- 結果表格、迴歸係數、統計圖,永不加裝飾性動畫;只允許「逐欄/逐列揭示」這種服務講解的動畫。
- 每一個動畫都應對應講者的一個「說話節拍」。講稿裡沒有停頓點的地方,就不該有動畫。

完整原則與每種版型的建議,讀 `references/animation-principles.md`。

## 工作流程

### 第 1 步:確認內容已定稿

本 skill 不做內容決策。若使用者的簡報內容還沒定(還在想說什麼、順序怎麼排),
先走 academic-pptx 的內容規劃,拿到定稿大綱後再回來。內容已定就直接進第 2 步。

### 第 2 步:撰寫 slides_content.json

依 `references/slides-content-schema.md` 的完整規格撰寫。最小骨架:

```json
{
  "metadata": { "presentation_title": "...", "author": "...", "version": "1.0.0" },
  "global_settings": {
    "aspect_ratio": "16:9",
    "theme_color": { "primary": "#0F172A", "secondary": "#38BDF8", "accent": "#F59E0B" },
    "font_family_east_asian": "Microsoft JhengHei"
  },
  "slides": [
    {
      "slide_id": 1,
      "layout": "cover",
      "engine_config": { "engine": "html-canvas", "fx": "particle-burst", "fx_intensity": "medium" },
      "content": { "headline": "主標題", "sub_headline": "副標題" }
    }
  ]
}
```

重要欄位速查:
- `engine_config.engine`:`html-canvas` 或 `native-pptx`。整份簡報通常選一種;混用時各引擎只輸出屬於自己的頁面。
- `engine_config.fx`:canvas 特效名(`particle-burst` / `drift-field` / `network-lines` / `none`)。只在 cover、section_divider、closing 版型生效,其他版型會被引擎忽略並警告。
- `elements[].animation`:`{ "entry_order": 1, "effect": "fade-in", "duration_ms": 500, "delay_ms": 0, "trigger": "on-click" }`。
- `content.bullets[].animation_step`:條列逐步揭示的步驟編號;同編號同步出現。
- `engine_config.post_process: "split-animation-layers"`:native-pptx 引擎的拆頁指令,轉 PDF 前用。

### 第 3 步:執行引擎

引擎 A(HTML-Canvas),零第三方依賴,任何有 Python 的環境都能跑:

```bash
python scripts/build_html_deck.py slides_content.json -o deck.html
```

引擎 B(Native-PPTX),需要 `python-pptx`(`pip install python-pptx`):

```bash
# 產出含原生動畫的 pptx
python scripts/build_native_pptx.py slides_content.json -o deck.pptx

# 拆頁模式:逐步動畫拆成連續頁面(轉 PDF 用,PPspliT 概念)
python scripts/build_native_pptx.py slides_content.json -o deck_print.pptx --split
```

### 第 4 步:驗證與交付

- HTML:用瀏覽器打開,←/→ 或空白鍵換頁、換頁內點擊觸發逐步揭示;`P` 鍵切換簡報者模式(含備忘稿)。
- PPTX:先用 python-pptx 重新開啟確認檔案合法,再提醒使用者用 PowerPoint 實際播放一次確認動畫。
  動畫時序不對時,調 JSON 的 `entry_order` / `delay_ms` 重跑即可,不要手動改 pptx。
- 拆頁版:確認頁數 =「原頁數 + 各頁動畫步數總和」(每頁 K 步拆成 K+1 頁,含未點擊的初始狀態),匯出 PDF 後排版不重疊。

## 兩引擎的能力邊界(如實告知使用者)

| 能力 | html-canvas | native-pptx |
|---|---|---|
| 粒子特效 | ✅ 三種,可調強度 | ❌(原生 PPT 做不到,勿承諾) |
| 物件進場動畫 | ✅ CSS 級(fade/fly/wipe/zoom) | ✅ 原生(appear/fade/wipe/fly-in) |
| 進場時序(順序+延遲) | ✅ | ✅(entry_order → 點擊組;delay_ms → 組內延遲) |
| 交出去可再編輯 | ❌(HTML 原始碼) | ✅(正常 PowerPoint 物件) |
| 動畫拆頁轉 PDF | 不需要(直接列印模式) | ✅ `--split` |
| 圖表 | 建議貼靜態圖(PNG/SVG) | 原生 shape 組合或貼圖 |

native-pptx 的動畫是以 OOXML `<p:timing>` 時間樹直接注入(python-pptx 沒有動畫 API)。
支援的效果清單與對應 presetID 寫死在 `scripts/build_native_pptx.py` 的 `EFFECT_MAP`,
新增效果前先讀該檔案開頭的註解,不要憑記憶編 presetID。

## 環境備註

- 兩支腳本都相容 Claude Code(桌面版)與 claude.ai 網頁版的程式執行環境;引擎 A 只用標準函式庫。
- Windows 中文字型預設「微軟正黑體」,可在 `global_settings.font_family_east_asian` 覆寫(如 DFKai-SB 標楷體)。
- 產出檔案一律 UTF-8;JSON 內中文不需轉義。
