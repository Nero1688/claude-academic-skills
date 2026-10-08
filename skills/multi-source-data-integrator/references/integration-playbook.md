# 多源整合實務手冊(語法骨架與檢查清單)

工具中立:R(dplyr/fuzzyjoin)或 Python(pandas/recordlinkage)皆可;示範用 Python,
概念一致。核心不是套件,是**紀律**:先訂規則、留譜系、報損耗。

## 1. 實體解析骨架(以統編為主鍵、代號×期間為輔)

```python
import pandas as pd

# 各源先各自 wrangle 乾淨(交 tej-data-wrangler),再進來整合
tej  = pd.read_parquet("tej_panel.parquet")     # 有 coid(代號)、year、財務欄
mops = pd.read_parquet("mops_events.parquet")   # 有 stock_id、event_date、subject

# (a) 統一主鍵:優先用統編(uni_no);沒有時用「代號×期間」防代號重用
#     對照表 xref: 由公司基本資料(統編↔代號↔起訖期間)建立,人工複核過
xref = pd.read_csv("firm_xref.csv")  # uni_no, coid, valid_from, valid_to, verified
def attach_unino(df, code_col, date_col):
    m = df.merge(xref, left_on=code_col, right_on="coid", how="left")
    # 期間過濾:事件/觀察日落在該代號的有效區間內
    m = m[(m[date_col] >= m["valid_from"]) & (m[date_col] <= m["valid_to"].fillna("2100-01-01"))]
    return m

# (b) 名稱模糊比對(僅在無代號/統編時;必人工複核)
# import recordlinkage  # 正規化公司名→候選配對→人工確認 verified=True 才用
```

## 2. 值調解規則表(事前訂,寫進方法節)

| 變數類 | 主源(優先) | 次源 | 容差 | 衝突處理 |
|---|---|---|---|---|
| 查核後財務數字 | 財報(MOPS/TEJ 財報) | TEJ 加工欄 | 單位四捨五入 | 超容差→標記人工判讀 |
| 即時事件日 | MOPS 重大訊息 | 媒體 | 0(日期) | 不一致→以官方揭露為準 |
| 長期報酬序列 | TEJ / TWSE | — | — | 缺值→標記,不跨源補 |
| 治理結構 | MOPS 董監揭露 | TEJ 治理模組 | — | 定義差→對齊操作型定義 |

```python
# 調解:主源優先,超容差進衝突清單
merged = tej.merge(mops_fin, on=["uni_no","year"], suffixes=("_tej","_mops"))
merged["conflict"] = (merged["asset_tej"] - merged["asset_mops"]).abs() > TOL
conflicts = merged[merged["conflict"]]        # 人工判讀,不自動平均
merged["asset"] = merged["asset_mops"]        # 主源=財報揭露
merged["asset_src"] = "MOPS財報"
print(f"衝突率 {merged['conflict'].mean():.1%}")  # >5% 回頭查對接錯配
```

## 3. 來源譜系欄位規格

```python
# 每個實質變數配 _src(來源)與 _asof(擷取/揭露時點)
# 例:tobinq, tobinq_src="TEJ", tobinq_asof="2026-07-01"
#     tnfd_event, tnfd_event_src="MOPS", tnfd_event_asof="2024-03-15"
# 免費源務必存 _asof:端點會變、公告會更正,靠它重建快照
```

資料附錄「來源清單表」模板:

| 來源 | 版本/擷取日 | 涵蓋範圍 | 提供變數 | 授權 |
|---|---|---|---|---|
| TEJ IFRS Finance | 2026-07 匯出 | 上市櫃 2016–2024 | 財務面板 | 訂閱 |
| MOPS 重大訊息 | 2026-07 擷取 | 上市櫃興櫃 | 事件日 | 官方公開 |

## 4. 三角驗證與合併損耗(投稿必附)

```python
# 收斂效度:同構念兩源相關
print(merged[["esg_tej","esg_mops"]].corr())     # 低相關要解釋

# 跨源抽樣一致率(人工核對 30 筆)
sample = merged.sample(30, random_state=20260723)
sample.to_csv("cross_check_30.csv")              # 人工填一致與否,報一致率

# 合併損耗對帳
print(f"TEJ 原始 {len(tej)} → 內連結 {len(merged)} → 損耗 {len(tej)-len(merged)}")
# 選擇偏誤:掉的 vs 留的 規模/產業分布比較
```

## 5. 出廠檢查清單(交下一棒建模前)

- [ ] 對接對照表已建、高風險配對人工複核
- [ ] 值調解規則事前訂、寫進方法節、衝突率已報
- [ ] 每實質變數有 _src / _asof 譜系欄
- [ ] 三角驗證(收斂相關 + 抽樣一致率)已跑
- [ ] 合併損耗對帳 + 選擇偏誤診斷已做
- [ ] 資料附錄來源清單表已備(投稿用)
- [ ] 整合後跑 thesis-consistency-audit 確認樣本數全篇一致
- [ ] 取得順序事前宣告;`_src` 記**實際供數**的來源;取數失敗與真實缺值已分開記錄(見第 6 節)

## 6. 取得層:降級順序、健康狀態與內容驗收(撈的當下就要留證據)

工序 2 的「來源優先序」處理**拿到了但不一致**;本節處理更早一步的**拿不拿得到**。
兩者要分開訂、分開寫進方法節。

1. **事前宣告取得順序**:每個變數寫明主源與備援(例:官方 API → 官方批次檔 → 鏡像或包裝層)。
   備援順序和值調解規則一樣,看了結果才改=資料操弄。
2. **`_src` 記實際供數者,不是計畫中的主源**:主源掛掉改用備援時,那幾格的 `_src`
   就是備援,另記 `_fetch_note`(為何降級)。審稿人問「這數字哪來的」,答案要是真的。
3. **備援上場要做重疊期對帳**:主源與備援在同一期抽樣比對,報一致率;沒對過帳的,
   不得把兩段無縫拼成一條序列——拼接點就是潛在的結構斷點。
4. **健康狀態分級**:可取數/需註冊/暫時性失敗(逾時、5xx、429,可退避重試)/
   永久性失敗(404、401、主機不存在,重試無益)。單一來源失敗不應讓整批中止,
   但每次失敗都進取數日誌。
5. **內容驗收**:HTTP 200 但結果是空的、或回來的是 HTML 說明頁/驗證頁,記為
   **取數失敗**,不是「該公司-期沒有資料」。混在一起的話,失敗會被誤當成合併損耗或真實缺值,
   污染工序 5 的選擇偏誤診斷。
6. **使用者強制指定來源時**:指定的來源不存在就忽略並記錄,不能因為一個寫錯的設定,
   把其他可用來源一起藏起來。

```python
SOURCES = {"cpi": ["official_api", "official_bulk", "mirror"]}   # 事前宣告,寫進方法節

def fetch_with_fallback(var, fetchers, log, asof):
    for src in SOURCES[var]:
        status, df = fetchers[src]()                  # status: ok / need_key / transient / permanent
        log.append({"var": var, "src": src, "status": status, "asof": asof})
        if status == "ok" and validate(df):           # 驗收:預期欄位齊、非空、值域合理
            df[f"{var}_src"], df[f"{var}_asof"] = src, asof
            return df
    return None   # 全數失敗:記為「取數失敗」,不要當成缺值填補
```

---

## 來源與授權

- 第 6 節(2026-10-08 新增)借鏡 **Panniantong/Agent-Reach**(MIT,
  https://github.com/Panniantong/Agent-Reach)的設計概念:有序的後端候選清單與
  「實際供數者」標記、實際執行的健康探測、區分缺失/損壞/逾時並只對暫時性失敗重試、
  「退出碼 0 但欄位為空不算成功」、使用者覆寫值無效時不得遮蔽可用後端。
  **其 cookie、登入態與帳號相關機制一律未借**;未使用其程式碼,範例為自行撰寫。
- 「缺少證據是未知、不是空」的紀律另參 **morluto/rea**(MIT,https://github.com/morluto/rea)。
