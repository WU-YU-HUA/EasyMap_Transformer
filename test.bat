@echo off
echo [1/2] 正在 tina 環境啟動 Streamlit...
start /b C:\Users\harry_wu\AppData\Local\anaconda3\envs\tina\python.exe -m streamlit run app.py

echo.
echo 等待 3 秒鐘讓 Streamlit 暖機...
timeout /t 3 > nul

echo.
echo [2/2] 正在啟動 Cloudflare 通道...
cloudflared tunnel --url http://127.0.0.1:8501
pause