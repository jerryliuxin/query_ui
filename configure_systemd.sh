#!/bin/bash
# 配置 Query UI 系统级 systemd 服务（需要 sudo）

set -e

echo "=== 配置 Query UI 系统级 Service ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 1. 创建服务文件
SERVICE_FILE="/etc/systemd/system/query_ui.service"

if [ -f "$SERVICE_FILE" ]; then
    echo "⚠️  服务文件已存在，备份为 ${SERVICE_FILE}.bak"
    sudo mv "$SERVICE_FILE" "${SERVICE_FILE}.bak"
fi

sudo tee "$SERVICE_FILE" > /dev/null << 'EOF'
[Unit]
Description=Query UI - Investment Research Knowledge Base (Production)
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/mickey/.openclaw/mihua/tools/query_ui
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8899
Restart=always
RestartSec=5
User=mickey
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "✅ 服务文件已创建: $SERVICE_FILE"

# 2. 重载 systemd 配置
sudo systemctl daemon-reload
echo "✅ systemd 配置已重载"

# 3. 停止用户级服务（避免端口冲突）
echo "🛑 停止用户级服务..."
systemctl --user stop query_ui_prod 2>/dev/null || true
systemctl --user disable query_ui_prod 2>/dev/null || true
echo "✅ 用户级服务已停止"

# 4. 启用并启动系统级服务
sudo systemctl enable query_ui
echo "✅ 开机自启已启用"

sudo systemctl restart query_ui
echo "✅ 服务已启动"

# 5. 查看状态
echo ""
echo "=== 服务状态 ==="
sudo systemctl status query_ui --no-pager

# 6. 测试端点
echo ""
echo "=== 端点测试 ==="
sleep 2
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8899/health | grep -q 200; then
    echo "✅ http://127.0.0.1:8899/health"
else
    echo "❌ 健康检查失败"
fi

echo ""
echo "🎉 配置完成！"
echo "   访问地址: http://192.168.100.45:8899/"
echo "   管理命令: sudo systemctl {start,stop,restart,status} query_ui"
echo "   日志查看: sudo journalctl -u query_ui -f"
