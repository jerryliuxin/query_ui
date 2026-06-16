#!/bin/bash
# Query UI 部署脚本：等待前端构建完成，然后启动生产服务

set -e

cd /home/mickey/.openclaw/mihua/tools/query_ui

echo "=== Query UI 部署开始 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 1. 检查前端是否已构建
if [ ! -f "frontend/dist/index.html" ]; then
    echo "⏳ 前端尚未构建，等待 dist/index.html 生成..."
    echo "   构建命令: cd frontend && npm run build"
    echo "   你可以另开终端执行上述命令，或等待自动完成..."
    
    # 等待构建完成（超时 10 分钟）
    timeout=600
    while [ $timeout -gt 0 ]; do
        if [ -f "frontend/dist/index.html" ]; then
            echo "✅ 检测到构建完成！"
            break
        fi
        sleep 5
        timeout=$((timeout-5))
        echo -n "."
    done
    echo
    
    if [ ! -f "frontend/dist/index.html" ]; then
        echo "❌ 超时：前端未构建完成，请手动执行 npm run build"
        exit 1
    fi
else
    echo "✅ 前端已构建 (frontend/dist/)"
fi

# 2. 停止现有服务
echo "🛑 停止现有服务..."
pkill -f "uvicorn.*app:app" 2>/dev/null || true
sleep 2

# 3. 启动生产服务
echo "🚀 启动生产服务 (端口 8899)..."
nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8899 > query_ui_prod.log 2>&1 &

# 记录 PID
echo $! > query_ui.pid
sleep 3

# 4. 验证服务
echo "🔍 验证服务..."
if ps -p $(cat query_ui.pid) > /dev/null; then
    echo "✅ 服务已启动 (PID $(cat query_ui.pid))"
else
    echo "❌ 服务启动失败"
    exit 1
fi

# 5. 测试端点
echo "📡 测试 API 端点..."
test_urls=(
    "http://192.168.100.45:8899/health"
    "http://192.168.100.45:8899/api/companies?page_size=1"
    "http://192.168.100.45:8899/api/stats/dashboard"
)

for url in "${test_urls[@]}"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    if [ "$code" = "200" ]; then
        echo "  ✅ $url"
    else
        echo "  ❌ $url (HTTP $code)"
    fi
done

echo ""
echo "🎉 Query UI 部署完成！"
echo "   访问地址: http://192.168.100.45:8899/"
echo "   API 文档: http://192.168.100.45:8899/docs"
echo "   PID 文件: $(pwd)/query_ui.pid"
echo "   日志查看: tail -f $(pwd)/query_ui_prod.log"
echo ""
echo "   停止服务: kill $(cat query_ui.pid)"
echo "   重启服务: $0 (再次运行此脚本)"
echo ""
echo "=== 完成时间: $(date '+%Y-%m-%d %H:%M:%S') ==="
