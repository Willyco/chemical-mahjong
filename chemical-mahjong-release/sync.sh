#!/bin/bash
# 化学麻将 Skill 自动同步脚本
# 使用方式：./sync.sh "更新说明"

SKILL_DIR="$HOME/.qclaw/workspace/chemical-mahjong-release"
WORKING_SKILL="$HOME/.qclaw/workspace/skills/chemical-mahjong"
WORKING_GAME="$HOME/.qclaw/workspace/chemical_mahjong"

echo "🔄 开始同步..."

cd "$SKILL_DIR" || exit 1

# 同步文件
[ -f "$WORKING_SKILL/SKILL.md" ] && cp "$WORKING_SKILL/SKILL.md" "$SKILL_DIR/SKILL.md" && echo "  ✅ SKILL.md"
[ -f "$WORKING_GAME/game.py" ] && cp "$WORKING_GAME/game.py" "$SKILL_DIR/game.py" && echo "  ✅ game.py"
[ -f "$WORKING_GAME/helper.py" ] && cp "$WORKING_GAME/helper.py" "$SKILL_DIR/helper.py" && echo "  ✅ helper.py"

# 检查更改
if git diff --quiet && git diff --staged --quiet; then
    echo "📝 没有新的更改"
    exit 0
fi

# Commit
COMMIT_MSG="${1:-更新skill}"
git add .
git commit -m "$COMMIT_MSG"
echo "  ✅ 已提交: $COMMIT_MSG"

# Push
echo "🚀 推送到GitHub..."
git push origin main

echo ""
echo "✅ 同步完成！"
echo "📦 https://github.com/Willyco/chemical-mahjong"
