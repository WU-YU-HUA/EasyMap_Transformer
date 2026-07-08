Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' 1. 直接呼叫 tina 環境裡的 python.exe 來執行 streamlit
WshShell.Run "cmd /c C:\Users\harry_wu\AppData\Local\anaconda3\envs\tina\python.exe -m streamlit run app.py", 0, False

' 2. 啟動通道，並將完整的日誌先寫入 raw_log.txt 暫存檔
WshShell.Run "cmd /c cloudflared tunnel --url http://127.0.0.1:8501 > raw_log.txt 2>&1", 0, False

' 3. 讓腳本暫停 6 秒鐘 (6000 毫秒)，等待 Cloudflare 連線並生成網址
WScript.Sleep 6000

' 4. 自動讀取暫存檔，把含有網址的那行挑出來，存成乾淨的 url_log.txt
On Error Resume Next ' 防止檔案還沒準備好而報錯
Set inFile = fso.OpenTextFile("raw_log.txt", 1)
Set outFile = fso.CreateTextFile("url_log.txt", True)

Do Until inFile.AtEndOfStream
    line = inFile.ReadLine
    ' 如果這行文字裡面包含 trycloudflare.com，就寫入乾淨的檔案裡
    If InStr(line, "trycloudflare.com") > 0 Then
        outFile.WriteLine line
    End If
Loop

inFile.Close
outFile.Close