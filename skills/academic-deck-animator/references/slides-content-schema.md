# slides_content.json 完整規格(v1.1)

本規格改良自使用者 2026-07 的原始設計(v1.0,見 ATTRIBUTION.md),主要變更:
移除指向外部 GitHub repo 的 `skill_id` 欄位(v1.0 用它路由到第三方工具;v1.1 起本 skill 自包含,
由 `engine` + `fx` / `effect` 直接決定行為)。讀到帶 `skill_id` 的舊檔案時直接忽略該欄位,不要報錯。

## 頂層結構

```json
{
  "metadata": { ... },
  "global_settings": { ... },
  "slides": [ ... ]
}
```

## metadata(必填)

| 欄位 | 型別 | 說明 |
|---|---|---|
| `presentation_title` | string | 簡報標題,同時用作 HTML `<title>` 與 pptx 核心屬性 |
| `author` | string | 講者姓名 |
| `version` | string | 內容版本,建議 semver |
| `last_updated` | string | ISO 日期 |

## global_settings(必填)

| 欄位 | 型別 | 預設 | 說明 |
|---|---|---|---|
| `aspect_ratio` | `"16:9"` \| `"4:3"` | `"16:9"` | 影響 pptx 頁面尺寸與 HTML viewport 比例 |
| `theme_color.primary` | hex | `#0F172A` | 主色(深色,標題/背景) |
| `theme_color.secondary` | hex | `#38BDF8` | 輔色(強調框、連接線) |
| `theme_color.accent` | hex | `#F59E0B` | 點綴色(重點標記,少用) |
| `font_family_east_asian` | string | `Microsoft JhengHei` | 中文字型 |
| `font_family_latin` | string | `Calibri` | 西文字型 |

學術場合配色建議:主色取深藍/深灰系,飽和度低;accent 全簡報出現不超過每頁一處。

## slides[](至少一頁)

每頁的共通欄位:

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| `slide_id` | int | ✅ | 從 1 遞增,引擎依此排序 |
| `title` | string | ✅ | 頁標題(cover 版型例外,用 content.headline) |
| `layout` | string | ✅ | 版型,見下表 |
| `engine_config` | object | ✅ | 引擎與動效設定 |
| `content` | object | ✅ | 版型對應的內容,見各版型 |
| `speaker_notes` | string | — | 備忘稿;HTML 進簡報者模式,pptx 進 notes slide |

### engine_config

| 欄位 | 型別 | 說明 |
|---|---|---|
| `engine` | `"html-canvas"` \| `"native-pptx"` | 這頁走哪個引擎 |
| `fx` | string | canvas 特效:`particle-burst`(粒子爆發,開場衝擊)/ `drift-field`(緩慢漂浮微粒,沉穩)/ `network-lines`(節點連線網,適合「連結/網絡」主題)/ `none`。僅 html-canvas 引擎、僅 cover/section_divider/closing 版型生效 |
| `fx_intensity` | `"low"` \| `"medium"` \| `"high"` | 粒子數量與速度;學術場合預設 `low`,除非使用者明說要高 |
| `transition` | string | 頁間轉場:html 引擎支援 `smooth-fade` / `slide` / `none`;pptx 引擎支援 `fade` / `push` / `wipe` / `none`(對應原生轉場) |
| `animate_objects` | bool | native-pptx 是否啟用物件動畫(預設 true;false 時忽略所有 animation 欄位) |
| `post_process` | string | `"split-animation-layers"`:native-pptx 拆頁模式的頁級開關;CLI `--split` 等效於全部頁面開啟 |

### 版型與 content 結構

#### `cover`(封面)
```json
"content": {
  "headline": "主標題",
  "sub_headline": "副標題(機構、學位、日期)",
  "background": { "type": "gradient", "colors": ["#0F172A", "#1E293B"] }
}
```
`background.type`:`gradient` / `solid`(配 `color`)。

#### `section_divider`(章節分隔頁)
```json
"content": { "section_number": "II", "headline": "研究方法" }
```

#### `bullet_points`(條列)
```json
"content": {
  "bullets": [
    { "text": "第一點", "animation_step": 1, "level": 0 },
    { "text": "子點", "animation_step": 1, "level": 1 },
    { "text": "第二點", "animation_step": 2 }
  ]
}
```
`animation_step` 相同者同步出現;省略 = 隨頁面直接顯示(不動畫)。`level` 0/1 兩層。
學術克制原則:一頁超過 5 個 animation_step 就是連環動畫破綻,重新分頁。

#### `architecture_chart`(架構圖/研究框架)
```json
"content": {
  "background": { "type": "solid", "color": "#FFFFFF" },
  "elements": [
    {
      "id": "node_01",
      "type": "shape_box",
      "text": "自變數:家族控制",
      "position": { "x": 1.0, "y": 1.5, "w": 3.5, "h": 1.0 },
      "style": { "fill": "#38BDF8", "font_size": 18, "color": "#FFFFFF" },
      "animation": { "entry_order": 1, "effect": "fade-in", "duration_ms": 500, "delay_ms": 0 }
    }
  ],
  "connections": [
    { "from": "node_01", "to": "node_02", "type": "flow_line", "label": "H1 (+)",
      "animation": { "entry_order": 3, "effect": "wipe", "duration_ms": 400 } }
  ]
}
```
- `position` 單位:英吋,原點左上;16:9 頁面為 13.333 × 7.5 吋。
- `type`:`shape_box`(圓角矩形)/ `text_label`(無框文字)。
- `connections.type`:`flow_line`(直線箭頭)/ `elbow`(直角折線箭頭)。
- 典型用法:假說模型逐步搭建——先自變數、再依變數、最後假說箭頭,每步配講解。

#### `two_column`(左右對照)
```json
"content": {
  "left":  { "heading": "既有文獻", "bullets": [ { "text": "..." } ] },
  "right": { "heading": "本研究",   "bullets": [ { "text": "..." } ] }
}
```

#### `figure_focus`(整頁圖)
```json
"content": { "image_path": "figures/fig1.png", "caption": "圖1 邊際效果", "fit": "contain" }
```
圖檔路徑相對於 JSON 所在目錄。HTML 引擎會把圖以 base64 內嵌(維持自包含)。

#### `closing`(結尾/致謝)
```json
"content": { "headline": "敬請指教", "contact": "email@example.edu" }
```

### animation(元素級)

| 欄位 | 型別 | 預設 | 說明 |
|---|---|---|---|
| `entry_order` | int | — | 進場順序組;同組同步。native-pptx 中每組=一次點擊 |
| `effect` | string | `fade-in` | `appear` / `fade-in` / `wipe` / `fly-in-from-bottom` / `fly-in-from-left` / `fly-in-from-right` |
| `duration_ms` | int | 500 | 動畫長度;學術場合 300–600 為宜 |
| `delay_ms` | int | 0 | 同組內相對延遲 |
| `trigger` | string | `on-click` | `on-click` / `after-previous`(native-pptx);html 引擎一律點擊/按鍵推進 |

## 引擎路由規則

1. 整份 JSON 只有一種 engine → 該引擎輸出全部頁面。
2. 混用 → 執行哪個引擎就輸出哪些頁;引擎會列出被跳過的 slide_id 提醒。
3. 一頁都不屬於執行中的引擎 → 報錯退出,提示使用者選對腳本。

## 與 v1.0 的欄位對照(讀舊檔用)

| v1.0(Word 檔原始設計) | v1.1 行為 |
|---|---|
| `engine_config.skill_id`(如 lewislulu/html-ppt-skill) | 忽略;engine+fx 已足夠 |
| `connections[].animation.skill_id` + `timeline_flow` | 忽略 skill_id;`timeline_flow: true` 視為 `effect: "wipe"` |
| `navigation: "smooth-fade"` | 改名 `transition`,值不變 |
| `layout: "bullet_points"` 的 `animation_step` | 完全相容 |
