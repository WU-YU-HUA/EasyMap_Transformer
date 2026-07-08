Set WshShell = CreateObject("WScript.Shell")
' 在背景啟動 Streamlit (0 代表隱藏視窗)
WshShell.Run "cmd /c streamlit run app.py", 0, False
' 在背景啟動 Cloudflare Tunnel
WshShell.Run "cmd /c cloudflared tunnel --url http://localhost:8501", 0, False