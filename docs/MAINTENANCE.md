# 維護與更新流程 / Maintenance

本 repo 的技能在維護者本機(Claude Code, `~/.claude/skills`)持續演進。要把最新版同步到本 repo:

```bash
# 在 repo 根目錄
python tools/update_from_local.py --src "C:/Users/<你>/.claude/skills"
bash scripts/sanitize_check.sh          # 必跑:公開前敏感掃描
git add -A && git commit -m "feat: sync skills to latest local version"
git push
```

`update_from_local.py` 會自動:排除不可重製的上游(check-citations)、套用合規版 SKILL.md、剝除訂閱版目錄內容、依「repo 外」的私密置換表去識別化、加上範例模板聲明。

> 私密樣式/置換表存放於 repo **之外**(建議與 repo 並排的 `PRIVATE_do_not_upload/`),不進版控。掃描腳本與更新腳本本身**不含任何個人資訊**。
