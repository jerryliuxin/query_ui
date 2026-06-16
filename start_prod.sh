#!/bin/bash
# 启动 Query UI 服务（生产模式）

cd /home/mickey/.openclaw/mihua/tools/query_ui

# 1. 确保前端已构建（优先检查 frontend_original，然后是 frontend）
if [ -d "frontend_original/dist" ]; then
    FRONTEND_DIR="frontend_original"
elif [ -d "frontend/dist" ]; then
    FRONTEND_DIR="frontend"
else
    echo "❌ 前端未构建，请先执行: (cd frontend_original && npm run build) 或 (cd frontend && npm run build)"
    exit 1
fi

# 2. 停止旧服务
pkill -f "uvicorn.*app:app" 2>/dev/null
sleep 1

# 3. 启动新服务（端口 8899）
nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8899 > query_ui_prod.log 2>&1 &
echo $! > query_ui.pid
sleep 2

# 4. 检查状态
if ps -p $(cat query_ui.pid) > /dev/null; then
    echo "✅ Query UI 已启动 (PID $(cat query_ui.pid))"
    echo "   访问地址: http://192.168.100.45:8899/"
    echo "   API 健康检查: http://192.168.100.45:8899/health"
else
    echo "❌ 启动失败，查看日志: tail -f query_ui_prod.log"
    exit 1
fi
