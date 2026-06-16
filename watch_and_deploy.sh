#!/bin/bash
# 自动检测 React 构建完成并部署

echo "监控前端构建进度..."
cd /home/mickey/.openclaw/mihua/tools/query_ui/frontend

# 等待 dist/index.html 生成且大于 1KB（避免只生成测试页）
while true; do
    if [ -f "dist/index.html" ]; then
        size=$(stat -c%s "dist/index.html" 2>/dev/null || echo 0)
        if [ $size -gt 1000 ]; then
            echo "✅ 检测到真实构建产物 (index.html: ${size} bytes)"
            break
        else
            echo "⏳ 发现测试页 (${size} bytes)，继续等待完整构建..."
        fi
    fi
    sleep 5
done

# 检查是否有 JS bundles
if ls dist/assets/*.js 2>/dev/null | grep -q .; then
    echo "✅ JS bundles 已生成"
else
    echo "⚠️  未发现 JS bundles，构建可能不完整"
fi

# 执行部署
echo ""
echo "开始部署..."
cd /home/mickey/.openclaw/mihua/tools/query_ui
./deploy_prod.sh
