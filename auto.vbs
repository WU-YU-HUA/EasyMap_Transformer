Set WshShell = CreateObject("WScript.Shell")

' 1. 在背景啟動 Streamlit
WshShell.Run "cmd /c streamlit run app.py", 0, False

' 2. 在背景啟動 Cloudflare Tunnel，並把輸出結果導向到 url_log.txt 檔案中 (2>&1 代表包含錯誤訊息)
WshShell.Run "cmd /c cloudflared tunnel --url http://localhost:8501 > url_log.txt 2>&1", 0, False