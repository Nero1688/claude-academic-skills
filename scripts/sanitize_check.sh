#!/usr/bin/env bash
# sanitize_check.sh — 公開前敏感資訊掃描(通用版)
# 用法: bash scripts/sanitize_check.sh [目標目錄]
# 個人化樣式(你的姓名、學號、機構名等)請放在 repo「外面」的私密檔:
#   ../PRIVATE_do_not_upload/private_patterns.txt   (每行一個 regex)
# 或以環境變數 SANITIZE_PRIVATE 指定路徑。私密檔絕不放進 repo。
set -u
ROOT="${1:-.}"
PRIVATE="${SANITIZE_PRIVATE:-$ROOT/../PRIVATE_do_not_upload/private_patterns.txt}"
hit=0
scan () {
  local label="$1"; local pattern="$2"
  local out
  out=$(grep -rniE --exclude-dir=.git --exclude="sanitize_check.sh" --exclude=".gitignore" "$pattern" "$ROOT" 2>/dev/null)
  if [ -n "$out" ]; then echo; echo "[HIT] $label"; echo "$out" | sed 's/^/    /'; hit=1; fi
}
echo "=== 敏感資訊掃描 (target: $ROOT) ==="
# 通用樣式(不含任何個人資訊)
scan "本機路徑"        "C:\\\\Users|/Users/[a-z]+/"
scan "認證檔/金鑰"      "auth\.json|api[_-]?key|secret[_-]?key|password|passwd|Bearer "
scan "疑似金鑰字串"     "sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}"
scan "訂閱來源標示"     "擷取自.*帳號|訂閱版導航"
scan "學號樣式"        "學號[::]? ?[0-9]{8,}"
# 私密樣式(從 repo 外讀入)
if [ -f "$PRIVATE" ]; then
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue; case "$pat" in \#*) continue;; esac
    scan "私密樣式" "$pat"
  done < "$PRIVATE"
else
  echo; echo "[i] 未找到私密樣式檔($PRIVATE),僅執行通用掃描。"
fi
echo
if [ "$hit" -eq 0 ]; then echo "OK: 未命中。仍建議人工複查 README 與各 SKILL.md。"; else echo "WARN: 有命中,請逐條確認後再 push。"; fi
exit $hit
