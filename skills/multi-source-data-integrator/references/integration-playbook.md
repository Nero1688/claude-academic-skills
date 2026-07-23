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
