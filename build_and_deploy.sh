#!/bin/bash
# 监控前端构建并自动部署

cd /home/mickey/.openclaw/mihua/tools/query_ui/frontend

echo "等待构建完成..."
while [ ! -f "dist/index.html" ]; do sleep 3; done

echo "✅ 检测到 dist/index.html"
echo "开始部署..."

cd /home/mickey/.openclaw/mihua/tools/query_ui
./deploy_prod.sh
