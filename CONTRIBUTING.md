# 貢獻指南 / Contributing

謝謝你願意貢獻！本專案供**非商業之學術交流**使用。

## 歡迎的貢獻
- 真實使用回饋、bug 回報（開 issue）
- 修正錯字、改善文件、補充使用範例
- **新增資料庫 profile**（WRDS/Compustat、CSMAR、World Bank…），見 [`docs/ADD_A_DATABASE.md`](docs/ADD_A_DATABASE.md)
- 新增台灣／華語學術脈絡的技能

## 三條底線
1. **資料由使用者自己合法取得。** 技能不得代抓資料、不得散布任何資料庫的**專屬完整目錄或欄位代碼全表**；只描述導覽方向並指向官方公開文件。
2. **尊重著作權。** 改作他人作品必附 `ATTRIBUTION.md` 並保留原授權，同步更新 `NOTICE.md`；上游無授權者不重製其程式碼。不重製受著作權保護的完整量表／問卷題項。
3. **不外洩個資與機構。** 不提交姓名、學號、機構帳號、金鑰、學校特定內部規則。送 PR 前務必執行：
   ```bash
   bash scripts/sanitize_check.sh
   ```

## 提交規範
- 每個技能一個資料夾，內含 `SKILL.md`。
- commit 訊息建議用 [Conventional Commits](https://www.conventionalcommits.org/)：`feat:`／`fix:`／`docs:`。
- 提交即表示：你原創的貢獻以根 `LICENSE` 釋出；改作他人作品的貢獻遵循其原授權。
