#!/bin/bash
# 自动同步skill到GitHub

SKILL_DIR="$HOME/.qclaw/workspace/chemical-mahjong-release"
WORKING_SKILL="$HOME/.qclaw/workspace/skills/chemical-mahjong"
WORKING_GAME="$HOME/.qclaw/workspace/chemical_mahjong"

cd "$SKILL_DIR"

# 同步最新的SKILL.md
if [ -f "$WORKING_SKILL/SKILL.md" ]; then
    cp "$WORKING_SKILL/SKILL.md" "$SKILL_DIR/SKILL.md"
    echo "✅ 已同步 SKILL.md"
fi

# 同步最新的game.py
if [ -f "$WORKING_GAME/game.py" ]; then
    cp "$WORKING_GAME/game.py" "$SKILL_DIR/game.py"
    echo "✅ 已同步 game.py"
fi

# 同步最新的helper.py
if [ -f "$WORKING_GAME/helper.py" ]; then
    cp "$WORKING_GAME/helper.py" "$SKILL_DIR/helper.py"
    echo "✅ 已同步 helper.py"
fi

# 检查是否有更改
if git diff --quiet && git diff --staged --quiet; then
    echo "📝 没有新的更改需要同步"
    exit 0
fi

# 获取commit信息
COMMIT_MSG="${1:-更新skill}"

# 提交并推送
git add .
git commit -m "$COMMIT_MSG"
git push origin main

echo "🚀 已同步到GitHub: https://github.com/Willyco/chemical-mahjong"
