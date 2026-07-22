import streamlit as st

# 設定首頁的頁面資訊
st.set_page_config(
    page_title="多功能資料處理工具箱",
    page_icon="👋",
    layout="centered"
)

st.title("👋 歡迎來到多功能資料處理工具箱")

st.markdown("""
這是一個整合型的資料處理服務。請從 **左側導覽列 (側邊欄)** 選擇您要使用的工具：

### 🛠️ 目前可用工具
* **[01] 🗺️ EasyMap 座標轉換**：將包含地政地址（如：段名、地號）的 Excel 檔案，自動批量查詢內政部 API，並轉換為 WGS84 與 TWD97 座標。
* **[02] 📄 PDF 分割工具**：將大型 PDF 檔案按照指定頁數或範圍進行分割，方便後續處理。
*(後續若有其他工具，只需將 Python 檔案放入 `pages/` 資料夾即可自動生成選單)*
""")