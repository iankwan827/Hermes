#!/bin/bash
# GitHub双向同步脚本 - Mac端
# 拉取Windows推送的更新，同时把Mac的变更推回去
# 用法：作为cron job每天执行，或手动运行

REPO_URL="https://github.com/iankwan827/Hermes.git"
SYNC_DIR="/tmp/hermes-sync-$$"
PROFILE_DIR="$HOME/.hermes/profiles/main"
REPORT=""

cleanup() {
    rm -rf "$SYNC_DIR" 2>/dev/null
}
trap cleanup EXIT

# 1. Clone仓库（shallow）
if ! git clone --depth=1 "$REPO_URL" "$SYNC_DIR" 2>/dev/null; then
    echo "❌ Git clone失败，检查网络或认证"
    exit 1
fi

# 2. 记录远程的commit信息
cd "$SYNC_DIR"
REMOTE_SHA=$(git rev-parse --short HEAD)
REMOTE_MSG=$(git log -1 --pretty=format:"%s (%ci)")
REPORT+="📥 远程最新: $REMOTE_SHA - $REMOTE_MSG\n"

# 3. 同步 skills（对比并更新有变化的）
UPDATED_SKILLS=()
for skill_dir in "$SYNC_DIR"/skills/*/; do
    [ ! -d "$skill_dir" ] && continue
    skill_name=$(basename "$skill_dir")
    
    # 处理子目录skill（如 bazi/bazi-analysis）
    for sub in "$skill_dir"/*/; do
        [ ! -d "$sub" ] && continue
        sub_name=$(basename "$sub")
        target="$PROFILE_DIR/skills/$skill_name/$sub_name"
        if [ -f "$sub/SKILL.md" ] && [ -d "$target" ]; then
            if ! diff -q "$sub/SKILL.md" "$target/SKILL.md" >/dev/null 2>&1; then
                cp "$sub/SKILL.md" "$target/SKILL.md"
                UPDATED_SKILLS+=("$skill_name/$sub_name")
            fi
        fi
    done
    
    # 处理顶层skill（如 bazi-sales-orchestrator）
    target="$PROFILE_DIR/skills/$skill_name"
    if [ -f "$skill_dir/SKILL.md" ] && [ -d "$target" ]; then
        if ! diff -q "$skill_dir/SKILL.md" "$target/SKILL.md" >/dev/null 2>&1; then
            cp "$skill_dir/SKILL.md" "$target/SKILL.md"
            UPDATED_SKILLS+=("$skill_name")
        fi
    fi
done

# 4. 同步 config.yaml、SOUL.md、memories
for f in config.yaml SOUL.md; do
    if [ -f "$SYNC_DIR/$f" ]; then
        if ! diff -q "$SYNC_DIR/$f" "$PROFILE_DIR/$f" >/dev/null 2>&1; then
            cp "$SYNC_DIR/$f" "$PROFILE_DIR/$f"
            REPORT+="📝 已更新: $f\n"
        fi
    fi
done

if [ -d "$SYNC_DIR/memories" ]; then
    for mem in "$SYNC_DIR"/memories/*; do
        [ ! -f "$mem" ] && continue
        mem_name=$(basename "$mem")
        if ! diff -q "$mem" "$PROFILE_DIR/memories/$mem_name" >/dev/null 2>&1; then
            cp "$mem" "$PROFILE_DIR/memories/$mem_name"
            REPORT+="📝 已更新: memories/$mem_name\n"
        fi
    done
fi

# 5. 输出结果
if [ ${#UPDATED_SKILLS[@]} -eq 0 ] && ! echo -e "$REPORT" | grep -q "已更新"; then
    echo "[SILENT]"
    exit 0
fi

echo "=== GitHub同步完成 ==="
echo ""
if [ ${#UPDATED_SKILLS[@]} -gt 0 ]; then
    echo "🔄 更新了 ${#UPDATED_SKILLS[@]} 个skill:"
    for s in "${UPDATED_SKILLS[@]}"; do
        echo "  - $s"
    done
fi
echo ""
echo -e "$REPORT"
echo ""
echo "⏰ 同步时间: $(date '+%Y-%m-%d %H:%M:%S')"
