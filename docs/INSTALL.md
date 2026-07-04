# 安裝說明 / Installation

Claude Skills 可掛在兩種環境。挑你用的那種即可。

## A. claude.ai（網頁 / 桌面 / App）

1. 於本 repo 首頁點 **Code → Download ZIP**，解壓縮。
2. 開 [claude.ai](https://claude.ai) → 左下或設定選單 → **Customize → Skills**。
3. 把 `skills/` 底下**你要的單一技能資料夾**（例如 `q1-journal-reviewer/`）壓成 zip，逐一上傳。
4. 到 **Settings → Capabilities**，開啟 **Code execution / File creation**
   （`management-figure`、`thesis-consistency-audit`、`check-citations` 等會跑腳本的技能需要）。
5. 確認技能出現在清單且為開啟狀態。

## B. Claude Code

技能放在 `~/.claude/skills/`（每個技能一個資料夾）。

```bash
git clone https://github.com/Nero1688/claude-academic-skills.git
mkdir -p ~/.claude/skills
# 複製你要的技能（可多個）
cp -r claude-academic-skills/skills/thesis-consistency-audit ~/.claude/skills/
cp -r claude-academic-skills/skills/q1-journal-reviewer      ~/.claude/skills/
```

部分技能有 Python 相依（如 `check-citations` 需要 `requests`）：

```bash
pip install requests python-docx matplotlib
```

## 使用

安裝後**不需特殊指令**，自然描述任務即可，Claude 會偵測情境自動載入：

- 「幫我對這份草稿做一致性稽核。」→ `thesis-consistency-audit`
- 「用 Q1 期刊審查委員角度審這篇。」→ `q1-journal-reviewer`
- 「把這個交互作用畫成出版級的圖。」→ `management-figure`

## 疑難排解

- **技能沒被觸發**：改用更貼近該技能「觸發詞」的說法（見 README 總覽表）。
- **腳本執行失敗**：確認已開啟 Code execution，且已安裝相依套件。
- **TEJ 相關技能**：需自備 TEJ 訂閱資料；本 repo 不含任何 TEJ 專屬資料檔。
