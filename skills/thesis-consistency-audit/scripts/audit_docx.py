"""
audit_docx.py — 管理／財務碩博論文「一致性稽核」機械對帳工具
審稿框架改作自 awesome_proofreading_auto by qqfly1to19 (CC BY-NC-SA 4.0),
已移除中文醫學術語庫與 GB/T 7714,重新瞄準管理/財務 + APA/TEJ。
僅依賴 python-docx。用法: python audit_docx.py <thesis.docx>
"""
import sys, re
import docx

NUM = re.compile(r"-?\d[\d,]*\.?\d*")
def to_f(s):
    s = s.replace(",", "").replace("(", "-").replace(")", "").strip()
    m = NUM.match(s.replace("-", "", 0) if False else s)
    try: return float(s)
    except: 
        mm = NUM.search(s)
        return float(mm.group().replace(",", "")) if mm else None

def grid(t):
    return [[c.text.strip().replace("\n", " ") for c in r.cells] for r in t.rows]

def check_totals(g, ti, out):
    # 找含「總計/合計/總」的列,驗證每個數值欄加總
    hdr = g[0]
    tot_rows = [i for i,r in enumerate(g) if any(k in (r[0] or "") for k in ("總計","合計","總"))]
    for tr in tot_rows:
        for col in range(1, len(hdr)):
            h = hdr[col] if col < len(hdr) else ""
            if any(k in h for k in ("%","比例","率","平均","中位","標準差","R²","R2")):
                continue
            vals = [to_f(g[i][col]) for i in range(1, tr) if i != tr]
            vals = [v for v in vals if v is not None]
            tot = to_f(g[tr][col]) if col < len(g[tr]) else None
            if tot is not None and vals and abs(sum(vals) - tot) > max(1.0, abs(tot)*0.005):
                out.append(f"  [表{ti}] 第{col}欄『{hdr[col][:12]}』加總={sum(vals):.0f} 與總計列 {tot:.0f} 不符")

def check_desc(g, ti, out):
    hdr = [h for h in g[0]]
    def col(name):
        for j,h in enumerate(hdr):
            if name in h: return j
        return None
    cN,cM,cS,cMin,cMed,cMax = (col("樣本數"),col("平均"),col("標準差"),col("最小"),col("中位"),col("最大"))
    if cMin is None or cMax is None: return None
    Ns=set()
    for r in g[1:]:
        name=r[0]
        mn,mx = to_f(r[cMin]) if cMin<len(r) else None, to_f(r[cMax]) if cMax<len(r) else None
        mean = to_f(r[cM]) if cM is not None and cM<len(r) else None
        sd = to_f(r[cS]) if cS is not None and cS<len(r) else None
        med = to_f(r[cMed]) if cMed is not None and cMed<len(r) else None
        n = to_f(r[cN]) if cN is not None and cN<len(r) else None
        if n is not None: Ns.add(int(n))
        if mn is not None and ("董事" in name or "BOARD" in name.upper()) and mn==0:
            out.append(f"  [表{ti}] 『{name[:16]}』最小值=0,董事會規模不應為0,疑遺漏值誤編")
        if None not in (mn,mx,mean,sd) and sd>0 and (mx-mean)/sd > 10:
            out.append(f"  [表{ti}] 『{name[:16]}』最大值{mx} 偏離平均{mean}達{(mx-mean)/sd:.0f}個SD,疑離群未縮尾")
        if None not in (mn,mx) and mn>mx:
            out.append(f"  [表{ti}] 『{name[:16]}』最小值>最大值,數據異常")
        if med is not None and None not in (mn,mx) and not (mn<=med<=mx):
            out.append(f"  [表{ti}] 『{name[:16]}』中位數不在[最小,最大]區間")
    return Ns

def find_reg_obs(g):
    for r in g:
        if r and any(k in r[0] for k in ("觀察值","Observations")) and "比例" not in r[0] and len(r)>1:
            vs=[int(to_f(c)) for c in r[1:] if to_f(c) is not None]
            if vs: return vs
    return []

def main(path):
    d = docx.Document(path)
    out=[]; desc_Ns=set(); reg_Ns=set()
    for ti,t in enumerate(d.tables):
        g=grid(t)
        check_totals(g, ti, out)
        ns=check_desc(g, ti, out)
        if ns: desc_Ns|=ns
        ro=find_reg_obs(g)
        if ro and any("R²" in (r[0] or "") or "R2" in (r[0] or "") for r in g):
            reg_Ns|=set(ro)
    if desc_Ns and reg_Ns:
        big_desc=max(desc_Ns); 
        for r in sorted(reg_Ns):
            if r < big_desc*0.95:
                out.append(f"  [N落差] 敘述統計樣本up to {big_desc} 但迴歸觀察值={r},少{big_desc-r}筆,需說明(常見為落後期/listwise)")
    print("=== 一致性稽核機械對帳 ===")
    print(f"敘述統計樣本數集合: {sorted(desc_Ns)}   迴歸觀察值集合: {sorted(reg_Ns)}")
    if out:
        print(f"\n發現 {len(out)} 項待查:")
        print("\n".join(out))
    else:
        print("未發現機械層面不一致(仍建議人工核對假設↔表、引用)。")

if __name__=="__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "thesis.docx")
