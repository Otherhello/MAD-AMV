@echo off
chcp 65001 >nul
cd /d "E:\MADAMV"
start "" "http://127.0.0.1:8080/"
echo 网站已尝试打开。请保持本窗口不要关闭。
echo 用完后按 Ctrl+C 或直接关闭窗口。
python server.py
if errorlevel 1 (
    echo.
    echo 启动失败。可改试：py server.py
    pause
)
