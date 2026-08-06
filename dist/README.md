# dist/ — 可直接安裝的個別技能包

這裡是每一支技能各自打包好的 `.zip`,**可直接上傳安裝**。
（`skills/` 是原始碼,`dist/` 是打包好的安裝檔;內容一致。）

## 為什麼不能「下載整個 repo 的 ZIP」直接裝?

GitHub 右上角 **Code → Download ZIP** 下載的是**整個 repo**
(`claude-academic-skills-main/skills/<34 支>/…`)——裡面有 34 個 `SKILL.md`、且深層巢狀。
Claude 的技能上傳一次只吃**一個技能**(壓縮檔頂層是單一技能資料夾、內含它的 `SKILL.md`)。
所以整包 repo ZIP 無法當「一個技能」上傳。**請改用本資料夾裡的個別 `.zip`。**

> 同理:claude.ai 的技能上傳是「上傳檔案」,**不能只給網址**讓它自己抓;
> 請先下載個別 `.zip` 檔,再上傳。

## 安裝(claude.ai)

1. 在本 `dist/` 資料夾點你要的技能 `.zip`(例 `literature-matrix-builder.zip`)→ 頁面右側 **Download**。
2. claude.ai → 右上頭像 → **Settings → Capabilities**,開啟 **Code execution**(有腳本的技能需要)。
3. **Settings → Skills → Add / Upload** → 選剛下載的 `.zip` → 完成。
4. 要幾支就重複幾次。上傳後跨裝置(桌面版/網頁版)自動同步。

## 安裝(Claude Code)

把 `skills/<名稱>/` 整個資料夾複製到 `~/.claude/skills/`(或專案的 `.claude/skills/`)即可,
不需打包。呼叫時技能名前加 `anthropic-skills:` 前綴。

## 一次裝多支?

Claude 目前一次上傳一個技能;要裝多支就逐一上傳(這是平台限制,非本包問題)。
建議先裝你當下研究流程用得到的幾支,其餘之後隨用隨加。
