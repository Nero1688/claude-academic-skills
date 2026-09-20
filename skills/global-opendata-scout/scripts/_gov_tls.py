#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_gov_tls.py — 政府／官方統計網站 TLS 相容層（本家族撈取腳本共用的單一正本）

【M2 修復（2026-09-20 資安審查）】
本檔原本只放在私人限定的 台灣官方統計的撈取腳本，但它是「防線」不是
「能力」——防止大家在遇到憑證錯誤時改用 `verify=False`，理應公開。三份實作
（台灣官方統計來源、global-opendata-scout/intl_fetch.py、
journal-submission-scout/journal_scout.py 各自內嵌一份）已經漂移：
intl_fetch.py 那份缺 `proxy_manager_for` 覆寫（公司機走 proxy 時不會套用這個
相容層），journal_scout.py 那份是內嵌在函式裡的區域類別。現在只留這一份正本，
`global-opendata-scout/scripts/_gov_tls.py` 改為指向本檔的 re-export 薄殼，
`intl_fetch.py`／`journal_scout.py` 改為從本檔匯入。

【為什麼需要這支】
Python 3.13 起，`ssl.create_default_context()` 預設開啟 OpenSSL 的嚴格憑證檢查
旗標 `VERIFY_X509_STRICT`（強制 RFC 5280 規範，例如 CA 憑證必須含
Subject Key Identifier 擴充欄位）。部分政府網站（尤其 .gov.tw）的憑證鏈不符合
該項規範，於是在新版 Python 會直接連線失敗，錯誤訊息為：

    SSLCertVerificationError: certificate verify failed:
    Missing Subject Key Identifier

實測（2026-07-24，Python 3.14.6 + requests 2.34.2 + certifi 2026.07.22）受影響者：
    - https://www.tpex.org.tw/       （台灣櫃買中心 OpenAPI）
    - https://plvr.land.moi.gov.tw/  （台灣內政部實價登錄批次下載）
不受影響者：
    - https://openapi.twse.com.tw/   （台灣證交所 OpenAPI）
    - https://data.gov.tw/           （台灣政府資料開放平臺）
升級 certifi 無效——這是伺服器端憑證的規範符合度問題，不是本機根憑證過期。
其他國家的政府/官方統計網站若出現同一症狀（Missing Subject Key Identifier），
本模組同樣適用；目前僅實測過台灣站點，其餘國家未實測前仍標「待確認」。

【本模組怎麼解】
只解除 `VERIFY_X509_STRICT` 這一個「RFC 規範嚴格度」旗標，
**完整保留**憑證鏈驗證與主機名稱驗證：
    verify_mode   = ssl.CERT_REQUIRED   （仍然驗證憑證）
    check_hostname = True               （仍然驗證主機名稱）

⚠️ 本模組**不使用** `verify=False`，也不呼叫 `urllib3.disable_warnings()`。
   那種做法會完全放棄憑證驗證、使連線可被中間人攻擊，
   且會觸發本 skill 家族發布前的資安掃描。修改本檔時請維持此原則。

【用法】
    from _gov_tls import make_session
    session = make_session()
    resp = session.get(url, timeout=30)

本檔也正確覆寫 `proxy_manager_for`（企業網路走 proxy 時，相容層才會套用到
proxy 連線，而不僅是直連時才生效——2026-09-20 修復前的 intl_fetch.py 內嵌版
缺這個覆寫，公司機透過 proxy 連線時會悄悄退回嚴格模式而連線失敗）。

last_verified: 2026-09-20
"""

from __future__ import annotations

import ssl

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.poolmanager import PoolManager
except ImportError:  # pragma: no cover - 由各呼叫端自行給出安裝提示
    raise


class _GovTLSAdapter(HTTPAdapter):
    """解除 VERIFY_X509_STRICT、但保留憑證與主機名驗證的 HTTPAdapter。"""

    def _build_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        # 只關掉 RFC 規範嚴格檢查；不動 verify_mode / check_hostname
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        return ctx

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        kwargs["ssl_context"] = self._build_context()
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block, **kwargs
        )

    def proxy_manager_for(self, proxy, **kwargs):
        kwargs["ssl_context"] = self._build_context()
        return super().proxy_manager_for(proxy, **kwargs)


def make_session() -> "requests.Session":
    """建立一個對受影響政府網站憑證相容、但仍完整驗證憑證的 requests.Session。"""
    session = requests.Session()
    session.mount("https://", _GovTLSAdapter())
    return session


def self_test() -> int:
    """對已知受影響與未受影響的站點各打一次，回傳失敗數（供人工驗證用）。"""
    targets = [
        ("TPEx 櫃買 OpenAPI", "https://www.tpex.org.tw/openapi/v1/tpex_index"),
        ("內政部實價登錄", "https://plvr.land.moi.gov.tw/DownloadOpenData"),
        ("證交所 OpenAPI", "https://openapi.twse.com.tw/v1/opendata/t187ap05_L"),
    ]
    session = make_session()
    failures = 0
    for name, url in targets:
        try:
            resp = session.get(url, timeout=30)
            print(f"OK   {name}: HTTP {resp.status_code}, {len(resp.content)} bytes")
        except Exception as exc:  # noqa: BLE001 - 自我測試需回報所有例外
            failures += 1
            print(f"FAIL {name}: {type(exc).__name__}: {str(exc)[:150]}")
    return failures


if __name__ == "__main__":
    import sys

    sys.exit(1 if self_test() else 0)
