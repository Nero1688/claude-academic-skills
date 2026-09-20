# 逐頁編號回饋格式(修訂迴圈)

本技能是離線批次引擎,不是即時預覽伺服器,所以不做「點選元素留言」那種互動式
介面。這份文件定義一套純文字的**逐頁編號回饋格式**,把「使用者對特定頁面提意見
→ 之後批次套用修改」的迴圈,落實成第 4 步驗證交付後、需要修訂時可重複執行的
流程。概念脈絡見 `ATTRIBUTION.md` 第 5 條(1weiho/open-slide)。

## 與 open-slide 的差異(定位澄清)

open-slide 讓使用者在開發伺服器裡直接點擊網頁上的元素、留言(如「make this
red」),留言以 `@slide-comment` 標記持久化在原始碼中,下次執行時批次套用。
本技能沒有開發伺服器、沒有即時預覽、也不在程式碼裡插標記,只借用「先收集
針對特定頁面的留言、再一次批次套用」這個迴圈概念,改寫成一份純文字回饋檔
＋一次 JSON 編輯＋一次重跑。

## 1. 回饋檔格式定義

每行一條,格式:

```
p<頁碼>: <修改指示>
```

- `<頁碼>` 對應 `slides_content.json` 裡該頁的 `slide_id`(見
  `references/slides-content-schema.md` 第 44-46 行,`slide_id` 為遞增整數)。
- `<修改指示>` 用自然語言即可,不必寫成程式碼或欄位名。
- 一份回饋檔可以有多行,對應多頁;同一頁若有多條指示,可寫多行同編號。

範例:

```
p3: 圖左移
p7: 拆兩頁
p12: 動畫改 fade
```

## 2. 回饋指示 → slides_content.json 欄位對應表

以下對應皆以 `slides-content-schema.md` 裡實際存在的欄位為準,規格沒有的欄位
一律不編造;規格不支援的指示,如實告知使用者「這個效果目前規格做不到」。

| 回饋類型(例句) | 對應欄位 | 備註 |
|---|---|---|
| 版面/位置(「圖左移」「框往上移」) | `content.elements[].position.x` / `.y`(單位英吋) | 僅 `architecture_chart` 版型有 `elements[]`;`figure_focus` 版型只有 `image_path`/`caption`/`fit`,規格沒有座標欄位,無法直接對應,需請使用者改用 architecture_chart 或另製圖檔。 |
| 拆頁(「拆兩頁」) | 在 `slides[]` 陣列新增一個 slide 物件 | 原條目的 `content.bullets` 或 `content.elements` 依語意切成兩組;新條目與其後所有頁面的 `slide_id` 依序 +1(schema 要求 slide_id 為遞增 int)。摘要裡用「p7b」這種人類可讀標籤指稱新頁,但 JSON 內仍是正常遞增整數,不寫入 "7b" 這種值。 |
| 動畫效果(「動畫改 fade」) | `content.elements[].animation.effect` 或 `content.connections[].animation.effect`,改成 `fade-in` | 只在 `architecture_chart` 版型有效。`bullet_points` 版型只有 `content.bullets[].animation_step`(分組同步揭示),規格沒有逐點 `effect` 欄位,不能真的套用「fade」視覺效果,只能調整揭示分組或建議換版型。 |
| 揭示節奏/順序(「這兩點同時出現」「晚一點出現」) | `content.bullets[].animation_step`(合併/拆開分組)或 `elements[].animation.entry_order` / `delay_ms` | 同一 `animation_step` 的 bullet 會同步出現。 |
| 特效/引擎(「這頁改用漂浮微粒」「換成 native-pptx」) | `engine_config.fx`(僅 cover/section_divider/closing 生效)或 `engine_config.engine` | 改 `engine` 等於整頁換引擎,需連動確認該頁其餘欄位仍相容。 |
| 備忘稿(「這頁補一句台詞」) | `speaker_notes` | 字串欄位,直接覆寫或附加。 |

## 3. 流程

1. 收到回饋檔(純文字,`.txt` 皆可),逐行解析出 `slide_id` 與修改指示。
2. 對每一行,依上表判斷指示屬於哪一類,找到 `slides_content.json` 裡
   `slide_id` 相符的條目,依對應欄位修改。拆頁類要連動調整後續所有
   `slide_id`。
3. 修改完成後,重新執行第 3 步的引擎指令(`build_html_deck.py` 或
   `build_native_pptx.py`)重新產出。
4. 輸出「本輪修改摘要」,逐頁列出改了什麼類別,方便使用者核對。
5. 若某條指示規格不支援(如對 bullet_points 套用 effect),在摘要裡明講
   「規格未提供該欄位,已略過/改用替代方案」,不要默默套用不存在的欄位。

## 4. 完整範例

### 4.1 回饋檔 `feedback_round1.txt`

```
p3: 圖左移
p7: 拆兩頁
p12: 動畫改 fade
```

### 4.2 修改前後片段(簡化示意)

p3 修改前(`architecture_chart` 版型,節點偏右):

```json
{
  "slide_id": 3,
  "layout": "architecture_chart",
  "content": {
    "elements": [
      { "id": "node_01", "type": "shape_box", "text": "自變數:家族控制",
        "position": { "x": 5.0, "y": 1.5, "w": 3.5, "h": 1.0 } }
    ]
  }
}
```

p3 修改後(x 從 5.0 改為 2.0,往左移 3 吋):

```json
      { "id": "node_01", "type": "shape_box", "text": "自變數:家族控制",
        "position": { "x": 2.0, "y": 1.5, "w": 3.5, "h": 1.0 } }
```

p7 修改前(`bullet_points` 版型,6 點擠在一頁):

```json
{
  "slide_id": 7,
  "layout": "bullet_points",
  "content": { "bullets": [
    { "text": "動機一", "animation_step": 1 },
    { "text": "動機二", "animation_step": 2 },
    { "text": "動機三", "animation_step": 3 },
    { "text": "缺口一", "animation_step": 4 },
    { "text": "缺口二", "animation_step": 5 },
    { "text": "缺口三", "animation_step": 6 }
  ]}
},
{ "slide_id": 8, "layout": "..." }
```

p7 修改後(拆成 slide_id 7 與新頁 slide_id 8,原 8 之後全部 +1):

```json
{
  "slide_id": 7,
  "layout": "bullet_points",
  "content": { "bullets": [
    { "text": "動機一", "animation_step": 1 },
    { "text": "動機二", "animation_step": 2 },
    { "text": "動機三", "animation_step": 3 }
  ]}
},
{
  "slide_id": 8,
  "layout": "bullet_points",
  "content": { "bullets": [
    { "text": "缺口一", "animation_step": 1 },
    { "text": "缺口二", "animation_step": 2 },
    { "text": "缺口三", "animation_step": 3 }
  ]}
},
{ "slide_id": 9, "layout": "..." }
```

p12 修改前(`architecture_chart` 版型,連接線效果為 wipe):

```json
"connections": [
  { "from": "node_01", "to": "node_02", "type": "flow_line", "label": "H1 (+)",
    "animation": { "entry_order": 3, "effect": "wipe", "duration_ms": 400 } }
]
```

p12 修改後(effect 改為 fade-in):

```json
"connections": [
  { "from": "node_01", "to": "node_02", "type": "flow_line", "label": "H1 (+)",
    "animation": { "entry_order": 3, "effect": "fade-in", "duration_ms": 400 } }
]
```

### 4.3 本輪摘要輸出範例

```
本輪修改:p3(版面,node_01 由 x=5.0 移至 x=2.0)、
        p7(拆頁,新增 p7b,原 slide_id 8 起全部 +1)、
        p12(動畫,connections effect: wipe → fade-in)
```
