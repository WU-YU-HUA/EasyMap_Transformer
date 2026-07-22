import streamlit as st
import pandas as pd
import requests
import time
import re
import io
from pyproj import Transformer
import base64
import urllib3 

# 告訴 urllib3 不要再顯示 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== 設定區 ====================
LAND_COLUMN = "addr"  # 你的 Excel 中，放地政地址的欄位名稱
TOKEN = "6ZUKCGSOPT8VMMCFZ6D7QU6MNT1OFH9W"  # 內政部 API Token

CITY_CODE = {
    "基隆市": "C", "臺北市": "A", "新北市": "F", "桃園市": "H",
    "新竹市": "O", "新竹縣": "J", "苗栗縣": "K", "臺中市": "B",
    "南投縣": "M", "彰化縣": "N", "雲林縣": "P", "嘉義市": "I",
    "嘉義縣": "Q", "臺南市": "D", "高雄市": "E", "屏東縣": "T",
    "宜蘭縣": "G", "花蓮縣": "U", "臺東縣": "V", "澎湖縣": "X",
    "金門縣": "W", "連江縣": "Z"
}

# ==================== 核心 API 函數 ====================

def get_town(city_code: str) -> list:
    url = f"https://easymap.moi.gov.tw/Z10Web/City_json_getTownList"
    data = {"cityCode": city_code, "struts.token.name": "token", "token": TOKEN}
    try:
        response = requests.post(url, data=data, timeout=10, verify=False)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"查詢縣市代碼 [{city_code}] 的鄉鎮區時發生錯誤: {e}")
    return []

def get_section(city_code: str, dist_code: str) -> list:
    url = f"https://easymap.moi.gov.tw/Z10Web/City_json_getSectionList"
    data = {"cityCode": city_code, "townCode": dist_code, "struts.token.name": "token", "token": TOKEN}
    try:
        response = requests.post(url, data=data, timeout=10, verify=False)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"查詢地段 [{city_code}, {dist_code}] 時發生錯誤: {e}")
    return []

def get_xy(section_code: str, office_code: str, land_number: str) -> tuple:
    url = f"https://easymap.moi.gov.tw/Z10Web/Land_json_locate"
    data = {"sectNo": section_code, "office": office_code, "landNo": land_number, "struts.token.name": "token", "token": TOKEN}
    try:
        response = requests.post(url, data=data, timeout=10, verify=False)
        if response.status_code == 200:
            res_json = response.json()
            return res_json.get("X", 0), res_json.get("Y", 0)
    except Exception as e:
        st.warning(f"查詢地號座標 [{section_code}, {land_number}] 時發生錯誤: {e}")
    return 0, 0

def get_xy_by_address(addr: str) -> tuple:
    # 1. 找縣市
    city_code = None
    city_name = ""
    for name, code in CITY_CODE.items():
        if name in addr:
            city_code = code
            city_name = name
            break
    if not city_code:
        return 0, 0

    # 2. 找鄉鎮區
    towns = get_town(city_code)
    town_code = None
    town_name = ""
    for t in towns:
        if t.get("name") in addr:
            town_code = t.get("id")
            town_name = t.get("name")
            break
    if not town_code:
        return 0, 0

    # 3. 找段名
    sections = get_section(city_code, town_code)
    section_code = None
    office_code = None
    section_name = ""
    for s in sections:
        if s.get("name") in addr:
            section_code = s.get("id")
            office_code = s.get("officeCode")
            section_name = s.get("name")
            break
    if not section_code:
        return 0, 0

    land_no_raw = addr.replace(city_name, "").replace(town_name, "").replace(section_name, "")

    # 4. 暴力提取最後一組數字
    matches = re.findall(r'[\d\-之]+', land_no_raw)
    if not matches:
        return 0, 0
    target_land_no = matches[-1].replace("之", "-")

    # 5. 格式化地號為 8 碼 (母號4碼 + 子號4碼)
    if "-" in target_land_no:
        main_no, sub_no = target_land_no.split("-")
    else:
        main_no, sub_no = target_land_no, "0"
    formatted_land_no = main_no.zfill(4) + sub_no.zfill(4)

    # 6. 呼叫 API 取得座標
    return get_xy(section_code, office_code, formatted_land_no)

def wgs84_to_twd97(x, y):
    if x == 0 or y == 0 or x == float('inf') or y == float('inf'):
        return 0, 0
    if not (119 < x < 123) or not (21 < y < 26):
        return 0, 0
    transformer = Transformer.from_crs("epsg:4326", "epsg:3826", always_xy=True)
    twd97_x, twd97_y = transformer.transform(x, y)
    return twd97_x, twd97_y

# ==================== Auto Download ====================
def auto_download_excel(excel_bytes: bytes, file_name: str = "easymap_processed.xlsx"):
    """
    利用 JavaScript 觸發瀏覽器自動下載 Excel 檔案，
    並在畫面上提供一個備用的手動下載按鈕。
    """
    # 1. 將檔案內容轉為 Base64 字串
    b64 = base64.b64encode(excel_bytes).decode()
    
    # 2. 建立 JavaScript 自動點擊下載的語法
    dl_link = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}'
    js_script = f"""
    <script>
        var a = document.createElement('a');
        a.href = "{dl_link}";
        a.download = "{file_name}";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    </script>
    """
    
    # 3. 執行 JavaScript 讓瀏覽器自動下載 (height=0 隱藏區塊)
    st.components.v1.html(js_script, height=0)

# ==================== Streamlit UI 介面 ====================

st.set_page_config(page_title="EasyMap 網頁版座標轉換工具", layout="centered")

st.title("🗺️ EasyMap 網頁版座標轉換工具")
st.markdown(f"請上傳包含地址欄位名稱為 **`{LAND_COLUMN}`** 的 Excel 檔案，系統會自動批量查詢內政部地政 API 並轉換為 WGS84 與 TWD97 座標。")

# 檔案上傳器
uploaded_file = st.file_uploader("選擇您的 Excel 檔案", type=["xlsx", "xls"])

if uploaded_file:
    # 預覽檢查檔案結構
    try:
        xls = pd.ExcelFile(uploaded_file)
        all_sheets = xls.sheet_names
        st.success(f"成功讀取檔案！共偵測到 {len(all_sheets)} 個工作表：{', '.join(all_sheets)}")
    except Exception as e:
        st.error(f"無法讀取該 Excel 檔案，請確認檔案格式是否正確。錯誤訊息: {e}")
        all_sheets = []

    # 開始處理按鈕
    if all_sheets and st.button("🚀 開始批量解析座標", type="primary"):
        # 建立記憶體內的 Excel 緩衝區
        output_buffer = io.BytesIO()
        
        try:
            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                # 逐個工作表處理
                for sheet_name in all_sheets:
                    st.write(f"---")
                    st.subheader(f"📊 正在處理工作表: {sheet_name}")
                    
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                    
                    if LAND_COLUMN not in df.columns:
                        st.warning(f"⚠️ 工作表【{sheet_name}】中找不到欄位 '{LAND_COLUMN}'，已跳過該工作表。")
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        continue
                    
                    new_rows = []
                    total_rows = len(df)
                    
                    # 建立該工作表的進度條與狀態文字
                    progress_bar = st.progress(0.0)
                    status_text = st.empty()
                    
                    for idx, row in df.iterrows():
                        raw_text = str(row[LAND_COLUMN]).strip() if pd.notna(row[LAND_COLUMN]) else ""
                        
                        status_text.text(f"進度: {idx+1}/{total_rows} | 正在解析: {raw_text}")
                        progress_bar.progress((idx + 1) / total_rows)
                        
                        if raw_text == "":
                            new_rows.append(row.to_dict())
                            continue
                        
                        # 呼叫座標轉換與 API
                        x, y = get_xy_by_address(raw_text)
                        nx, ny = wgs84_to_twd97(x, y)
                        
                        # 政府 API 防阻擋延遲
                        time.sleep(0.5)
                        
                        new_row = row.to_dict()
                        new_row['TWD97_X'] = round(nx, 3)
                        new_row['TWD97_Y'] = round(ny, 3)
                        new_row['WGS84_X'] = x
                        new_row['WGS84_Y'] = y
                        
                        new_rows.append(new_row)
                    
                    # 儲存該工作表結果
                    if new_rows:
                        output_df = pd.DataFrame(new_rows)
                        output_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        st.success(f"✨ 工作表【{sheet_name}】處理完畢！")
            
            st.write(f"---")
            st.balloons()
            st.success("🎉 全數檔案處理完成！請點選下方按鈕下載新檔案。")

            excel_bytes = output_buffer.getvalue()
            # ==================== 呼叫自動下載函式 ====================
            input_filename = uploaded_file.name
            dynamic_output_filename = f"easymap_{input_filename}"
            auto_download_excel(excel_bytes, dynamic_output_filename)
            # ==========================================================
            # 提供下載按鈕
            st.download_button(
                label="📥 下載轉換後的 Excel 檔案",
                data=output_buffer.getvalue(),
                file_name=dynamic_output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as process_error:
            st.error(f"處理過程中發生預期之外的錯誤: {process_error}")