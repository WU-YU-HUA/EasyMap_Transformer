# Streamlit 部署限制與多頁面架構 (Multipage App) 指南

本指南彙整了 Streamlit Community Cloud 的免費部署限制，以及如何將多個獨立的 Python 數據工具整合進同一個 Streamlit 應用程式中（自帶側邊欄漢堡選單）。

---

## 一、 Streamlit Community Cloud 免費帳號限制

在免費版的 Streamlit 雲端代管服務中，App 的數量限制取決於你綁定的 **GitHub 儲存庫 (Repository) 隱私設定**：

* **公開專案 (Public Repository)**：✅ **無數量限制！** 你可以部署無限多個 App。
* **私有專案 (Private Repository)**：🔒 **限制 1 個**。若程式碼含有機密不想公開，免費額度僅能部署一個私有 App。
* **硬體與休眠機制**：
  * 每個 App 約分配 **1GB RAM**。
  * 若 App 閒置數天無人造訪，系統會自動將其設為「休眠狀態」。下次造訪時需等待約 30~60 秒重新喚醒伺服器。

> **💡 實務建議：** 考量到私有專案限制與網址管理的便利性，強烈建議將多個輕量級的小工具（如報表轉換、座標查詢等）**合併成一個「工具箱 App」**。

---

## 二、 如何實作多頁面應用程式 (整合所有工具)

Streamlit 原生支援多頁面架構（Multipage Apps），**完全不需要手動撰寫前端的漢堡選單 (Burger Menu) 或複雜的 `import` 邏輯**。系統會自動在網頁左側生成美觀的導覽列。

目前有以下兩種主流的實作方式：

### 方案 A：使用原生的 `pages/` 資料夾結構 (最簡單推薦)

這是最直覺的做法，Streamlit 會自動讀取特定名稱的資料夾並生成選單。

**📁 專案資料夾結構範例：**
```text
my_toolbox_app/
├── app.py                         # 系統首頁 (例如：歡迎畫面、系統公告)
├── requirements.txt               # 依賴套件清單
└── pages/                         # ⚠️ 資料夾名稱必須是 'pages'
    ├── 01_🗺️_EasyMap座標轉換.py   # 工具 A (檔名前面的數字決定選單排序)
    ├── 02_📊_資料清洗工具.py        # 工具 B (Emoji 會自動顯示在選單上)
    └── 03_📝_報表自動產生器.py      # 工具 C