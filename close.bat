@echo off
echo 正在關閉 EasyMap 伺服器與連線通道...

:: 強制關閉所有的 Python 行程 (Streamlit)
taskkill /F /IM python.exe /T

:: 強制關閉 Cloudflare Tunnel
taskkill /F /IM cloudflared.exe /T

echo.
echo 伺服器已成功關閉！
pause