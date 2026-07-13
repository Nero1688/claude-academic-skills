# Python 第三軌:linearmodels 面板計量(2026-07 新增)

R/SPSS 之外的第三條軌道。**何時選 Python**:資料來自 tejapi 直撈(DataFrame 已在
Python 記憶體)、需要與資料清理管線(pandas)同一腳本完成、或使用者環境只有 Python。
統計功力等同 R plm;SPSS 使用者慣性強者仍走 SPSS。

套件:[bashtage/linearmodels](https://github.com/bashtage/linearmodels)(`pip install linearmodels`),
輔以 statsmodels(交乘、簡單斜率)。

## 標準骨架:雙向固定效果+叢集標準誤

```python
import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS, RandomEffects, compare

# ── 再現性聲明 ──
# Python 3.13 / pandas、linearmodels 版本用 pip freeze 記錄;seed 僅 bootstrap 需要
np.random.seed(20260710)

# ── 面板索引:MultiIndex(公司, 年) 是 linearmodels 的入場券 ──
df = df.set_index(["coid", "year"])            # coid=公司代碼, year 需為 int 或 datetime

# ── 前置資料檢查(紅旗關卡,原則同 SKILL.md Step 2)──
print(df[xvars].isna().mean())                  # 遺漏率
print(df[xvars].describe(percentiles=[.01, .99]))  # 極端值視察
corr = df[xvars].corr()
assert (corr.abs().values[np.triu_indices_from(corr, 1)] < 0.9).all(), "相關逾0.9紅旗"

# ── 主模型:公司+年度雙向 FE,叢集在公司 ──
mod = PanelOLS.from_formula(
    "roa ~ 1 + tnfd + esg_e + size + lev + EntityEffects + TimeEffects",
    data=df, drop_absorbed=True)
fe = mod.fit(cov_type="clustered", cluster_entity=True)
print(fe.summary)
```

## Hausman 檢定(FE vs RE)

linearmodels 沒有內建 Hausman,標準做法:

```python
re = RandomEffects.from_formula("roa ~ 1 + tnfd + esg_e + size + lev", data=df).fit()
b, B = fe.params, re.params
common = b.index.intersection(B.index).drop("Intercept", errors="ignore")
v = fe.cov.loc[common, common] - re.cov.loc[common, common]
d = (b - B)[common]
stat = float(d @ np.linalg.pinv(v) @ d)
from scipy import stats as st
print(f"Hausman χ²({len(common)}) = {stat:.3f}, p = {1 - st.chi2.cdf(stat, len(common)):.4f}")
# p < .05 → 拒絕 RE,採 FE(慣例判準;寫報告時仍需引用文獻)
```

## 調節(交乘項+簡單斜率)

```python
df["tnfd_x_esge"] = df["tnfd"] * df["esg_e_c"]   # esg_e_c = 中心化後的調節變數
mod = PanelOLS.from_formula(
    "q ~ 1 + tnfd + esg_e_c + tnfd_x_esge + size + lev + EntityEffects + TimeEffects",
    data=df).fit(cov_type="clustered", cluster_entity=True)

# 簡單斜率:M 取 -1SD / 均值 / +1SD 時,X 的邊際效果 = β1 + β3·M
for label, m in [("-1SD", -df.esg_e_c.std()), ("Mean", 0), ("+1SD", df.esg_e_c.std())]:
    beta = mod.params["tnfd"] + mod.params["tnfd_x_esge"] * m
    se = np.sqrt(mod.cov.loc["tnfd", "tnfd"]
                 + m**2 * mod.cov.loc["tnfd_x_esge", "tnfd_x_esge"]
                 + 2*m * mod.cov.loc["tnfd", "tnfd_x_esge"])
    print(f"{label}: b={beta:.4f}, t={beta/se:.2f}")
```

## 二次項轉折點

```python
# y ~ x + x²;轉折點 = -β1/(2β2),務必檢查轉折點是否落在樣本範圍內
tp = -mod.params["x"] / (2 * mod.params["x2"])
print(f"轉折點 {tp:.3f};樣本範圍 [{df.x.min():.3f}, {df.x.max():.3f}]")
```

## 與 tejapi 的無縫接軌(全 Python 管線)

```python
import os, tejapi
tejapi.ApiConfig.api_key = os.environ["TEJAPI_KEY"]     # 金鑰只走環境變數
raw = tejapi.get("TWN/<表代碼>", mdate={"gte": "2016-01-01"}, paginate=True)
# → tej-data-wrangler 清理原則(欄名標準化、頻率解析、winsorize)
# → 本檔建模 → management-figure 出圖
```

## 對帳紀律(同 SKILL.md Step 4)

樣本數(`fe.nobs`)、實體數(`fe.entity_info.total`)、係數與 SE 逐項抄進迴歸表後,
用 thesis-consistency-audit 的「敘述↔迴歸 N 對帳」核一次;linearmodels 的 nobs 是
「進入估計的觀察值」,與 df 原始列數之差=遺漏刪除數,要能解釋。
