# 維護流程 / Maintenance

改完技能、推送之前，請在 repo 根目錄跑這幾項檢查：

```bash
bash scripts/sanitize_check.sh      # 敏感資訊掃描（本機路徑、金鑰、學號樣式等）
bash scripts/security_scan.sh       # 資安掃描（危險執行、對外連線、混淆、憑證、提示注入）
python scripts/ci_checks.py .       # 結構一致性（NOTICE、技能數、frontmatter）
python scripts/build_dist.py        # 重建 dist/ 的個別安裝包
```

GitHub 上的 `guard` 工作流程每次 push 都會再跑一次同樣的檢查，任何一項沒過就會擋下。

個人化的掃描樣式（例如你的姓名、學號）請放在 repo 外面的檔案，用環境變數 `SANITIZE_PRIVATE` 指定路徑，不要放進版控。
