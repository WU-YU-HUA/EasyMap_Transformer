Set WshShell = CreateObject("WScript.Shell")

' 1. 直接呼叫 tina 環境裡的 python.exe 來執行 streamlit (絕對不會抓錯環境)
WshShell.Run "cmd /c C:\Users\harry_wu\AppData\Local\anaconda3\envs\tina\python.exe -m streamlit run app.py", 0, False

' 2. 讓腳本暫停 3 秒鐘，等待 Streamlit 完全啟動
WScript.Sleep 3000

' 3. 啟動通道，並透過 findstr 篩選，只把包含網址的那行存進 url_log.txt
WshShell.Run "cmd /c cloudflared tunnel --url http://127.0.0.1:8501 2>&1 | findstr ""trycloudflare.com"" > url_log.txt", 0, False