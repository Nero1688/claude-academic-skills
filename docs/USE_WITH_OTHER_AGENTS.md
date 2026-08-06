# 在其他 AI 代理上使用這些技能 / Using these skills with other agents

## TL;DR

好消息:**這些技能的格式與 OpenAI Codex 的技能格式幾乎相同**——都是「一個資料夾 +
根目錄 `SKILL.md`(YAML frontmatter 的 `name` / `description`)+ 選配 `scripts/`、
`references/`、`assets/`」,連「用 `description` 做隱式觸發」的機制都一樣。所以本包技能
**可直接裝到 Codex**,只是放到 Codex 的技能目錄、而非 Claude 的。無需轉檔。

Good news: **the skill format here is essentially the same as OpenAI Codex's** — a folder
with a root `SKILL.md` (YAML `name` / `description` frontmatter) plus optional `scripts/`,
`references/`, `assets/`, and the same "match on `description`" implicit invocation. So these
skills install on Codex directly — just into Codex's skills directory instead of Claude's.
No conversion needed.

---

## Claude(claude.ai / Claude Code)

- **claude.ai**:到 [`../dist/`](../dist/) 下載個別技能 `.zip` → Settings → Skills → Upload。
- **Claude Code**:把 `skills/<名稱>/` 複製到 `~/.claude/skills/`。呼叫時技能名前加
  `anthropic-skills:` 前綴。

## OpenAI Codex

Codex 也用 `SKILL.md`(同 `name` / `description` frontmatter)。安裝:把整個
`skills/<名稱>/` 資料夾放進 Codex 的技能目錄。依 OpenAI 官方文件,Codex 掃描下列位置
(以官方文件最新路徑為準,見文末連結):

| 範圍 | 路徑(依官方文件) |
|---|---|
| 個人跨專案 | `~/.agents/skills/<名稱>/` |
| 單一專案 | `<repo>/.agents/skills/<名稱>/` |

步驟:
1. 從本 repo 取 `skills/<名稱>/` 整個資料夾(或解壓 `dist/<名稱>.zip`)。
2. 放進上表任一目錄。Codex 自動偵測;沒出現就重啟。
3. 技能的 `description` 會被 Codex 用來隱式觸發,與 Claude 相同。

**跨代理的三個注意點:**
1. **呼叫前綴**:部分技能內文寫「Claude Code 呼叫加 `anthropic-skills:` 前綴」——那是
   Claude 專屬慣例,在 Codex 忽略即可,不影響技能內容。
2. **腳本**:`scripts/` 是純 Python,任何代理都能跑;`pip install` 的依賴一樣裝。
3. **選配設定**:Codex 支援選配的 `agents/openai.yaml` 做代理專屬設定,本包技能不需要
   也能用;要細調再加。

## 其他代理(通則)

任何能讀 markdown 指令 + 跑 Python 的代理,都能用技能的「內容」:
- 把 `SKILL.md` 的方法內文貼進該代理的指令/context(或其等價的 `AGENTS.md` 之類機制)。
- 直接使用 `scripts/` 與 `references/`。
- 差別只在「自動觸發」是否支援;不支援就手動指給它看。

## 官方文件連結(以官方最新為準)

- OpenAI Codex 技能:https://developers.openai.com/codex/skills
- OpenAI Codex AGENTS.md:https://developers.openai.com/codex/guides/agents-md
- 路徑與安裝方式可能隨版本更動,安裝前請對照官方文件當期說明。
