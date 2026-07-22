import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

st.set_page_config(page_title="PDF 分割工具", page_icon="📄")

st.title("📄 PDF 分割工具 (PDF-Editor)")
st.markdown("上傳您的 PDF 檔案，選擇裁切模式並輸入對應的條件。")

# 1. 檔案上傳區塊
uploaded_file = st.file_uploader("選擇要處理的 PDF 檔案", type=["pdf"])

# 2. 選擇模式與參數
mode = st.radio("選擇裁切模式", ["固定頁數裁切", "範圍裁切"], horizontal=True)

if mode == "固定頁數裁切":
    st.info("💡 範例：輸入 **2** -> 代表每 2 頁存成一個新的 PDF")
    user_input = st.text_input("請輸入固定頁數 (例如: 2)", "")
elif mode == "範圍裁切":
    st.info("💡 範例：輸入 **2-5** -> 代表將第 2 到第 5 頁獨立存成一個新的 PDF")
    user_input = st.text_input("請輸入範圍 (例如: 2-5)", "")

# 3. 執行按鈕與處理邏輯
if uploaded_file and user_input:
    if st.button("✂️ 準備裁切", type="primary"):
        try:
            # 將上傳的檔案讀取為 byte stream 提供給 PyMuPDF
            file_bytes = uploaded_file.read()
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            original_filename = uploaded_file.name.replace(".pdf", "")
            
            if mode == "固定頁數裁切":
                every_page = int(user_input)
                if every_page <= 0:
                    st.error("頁數必須大於 0")
                else:
                    pdf_list = []
                    # 進行固定頁數裁切
                    for page in range(0, len(doc), every_page):
                        end_page = min(page + every_page - 1, len(doc) - 1)
                        new_doc = fitz.open()
                        new_doc.insert_pdf(doc, from_page=page, to_page=end_page)
                        
                        # 將裁切後的 PDF 寫入記憶體
                        pdf_bytes_out = new_doc.write()
                        pdf_list.append((f"{original_filename}_{page+1}_{end_page+1}.pdf", pdf_bytes_out))
                        new_doc.close()
                    
                    # 將多個 PDF 打包成 ZIP
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for filename, file_data in pdf_list:
                            zip_file.writestr(filename, file_data)
                    
                    st.success(f"✅ 成功將 PDF 每 {every_page} 頁切割，共產生 {len(pdf_list)} 個檔案！")
                    st.download_button(
                        label="📦 點此下載 ZIP 壓縮檔",
                        data=zip_buffer.getvalue(),
                        file_name=f"{original_filename}_split.zip",
                        mime="application/zip"
                    )

            elif mode == "範圍裁切":
                # 解析輸入的範圍 (例如 "2-5")
                start_str, end_str = user_input.split("-")
                start = int(start_str.strip())
                end = int(end_str.strip())
                
                if start > end or start < 1 or end > len(doc):
                    st.error(f"輸入範圍錯誤！此 PDF 共有 {len(doc)} 頁，請確認輸入範圍。")
                else:
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=start-1, to_page=end-1)
                    
                    # 將裁切後的 PDF 寫入記憶體
                    pdf_bytes_out = new_doc.write()
                    new_doc.close()
                    
                    output_name = f"{original_filename}_{start}_{end}.pdf"
                    st.success(f"✅ 成功擷取第 {start} 到 {end} 頁！")
                    st.download_button(
                        label=f"📥 下載 {output_name}",
                        data=pdf_bytes_out,
                        file_name=output_name,
                        mime="application/pdf"
                    )
            
            # 關閉原始文件
            doc.close()
            
        except ValueError:
            st.error("⚠️ 輸入格式錯誤，請確認您輸入的是正確的數字或範圍（例如：2 或 2-5）。")
        except Exception as e:
            st.error(f"⚠️ 處理 PDF 時發生錯誤：{e}")