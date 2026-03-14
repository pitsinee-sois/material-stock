import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO

# --- การตั้งค่าพื้นฐาน ---
DB_FILE = "material_db.csv"
IMG_DIR = "material_images"
QR_DIR = "material_qrs"

for folder in [IMG_DIR, QR_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['Material', 'Category', 'Stock', 'Min_Stock', 'Image_Path'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# ฟังก์ชันสร้าง QR Code
def generate_qr(data_text, filename):
    qr = qrcode.make(data_text)
    path = os.path.join(QR_DIR, f"{filename}.png")
    qr.save(path)
    return path

# --- UI Setup ---
st.set_page_config(page_title="Material Master Pro", layout="wide")
st.title("🚀 Material Management System Pro")

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- ส่วนที่ 1: เพิ่ม/แก้ไขข้อมูล (Add & Update) ---
with st.sidebar:
    st.header("➕ จัดการข้อมูล")
    with st.form("material_form", clear_on_submit=True):
        name = st.text_input("ชื่อวัสดุ (Material Name)")
        cat = st.selectbox("หมวดหมู่", ['Wood', 'Metal', 'Fabric', 'Plastic', 'Glass', 'Other'])
        stock = st.number_input("จำนวนปัจจุบัน", min_value=0)
        min_stock = st.number_input("จุดแจ้งเตือน (Minimum Stock)", min_value=1, value=5)
        file = st.file_uploader("รูปภาพวัสดุ", type=['jpg', 'png'])
        
        submit = st.form_submit_button("บันทึกข้อมูล")
        
        if submit:
            if name:
                img_path = "None"
                if file:
                    img_path = os.path.join(IMG_DIR, f"{name}.png")
                    with open(img_path, "wb") as f:
                        f.write(file.getbuffer())
                
                # สร้าง QR Code อัตโนมัติ
                qr_path = generate_qr(f"Material: {name}, Cat: {cat}", name)
                
                new_row = {'Material': name, 'Category': cat, 'Stock': stock, 'Min_Stock': min_stock, 'Image_Path': img_path}
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"เพิ่ม {name} สำเร็จ!")
                st.rerun()

# --- ส่วนที่ 2: แสดงผลและตัวกรอง (Dashboard) ---
col_search, col_export = st.columns([3, 1])
with col_search:
    search = st.text_input("🔍 ค้นหาแมททีเรียล...")
with col_export:
    # ปุ่ม Export Excel
    csv = st.session_state.df.to_csv(index=False).encode('utf_8_sig')
    st.download_button("📥 Export CSV (Excel)", data=csv, file_name="inventory_report.csv", mime="text/csv")

# กรองข้อมูล
df_view = st.session_state.df
if search:
    df_view = df_view[df_view['Material'].str.contains(search, case=False, na=False)]

# --- ส่วนที่ 3: ตารางจัดการวัสดุ (Material Cards) ---
st.divider()
if not df_view.empty:
    # ส่วนหัวตารางแบบ Custom
    h1, h2, h3, h4, h5, h6 = st.columns([1, 2, 1, 1, 1, 1])
    h1.write("**รูปภาพ**")
    h2.write("**ชื่อวัสดุ**")
    h3.write("**หมวดหมู่**")
    h4.write("**คงเหลือ**")
    h5.write("**QR Code**")
    h6.write("**จัดการ**")
    st.divider()

    for idx, row in df_view.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 1, 1, 1, 1])
        
        with c1:
            if row['Image_Path'] != "None":
                st.image(row['Image_Path'], width=70)
            else:
                st.write("🖼️")
        
        with c2:
            st.write(f"**{row['Material']}**")
        
        with c3:
            st.caption(row['Category'])
        
        with c4:
            # ระบบ Low Stock Alert
            if row['Stock'] <= row['Min_Stock']:
                st.error(f"{row['Stock']} (Low!)")
            else:
                st.success(row['Stock'])
        
        with c5:
            qr_file = os.path.join(QR_DIR, f"{row['Material']}.png")
            if os.path.exists(qr_file):
                st.image(qr_file, width=50)
        
        with c6:
            if st.button("🗑️", key=f"del_{idx}"):
                st.session_state.df = st.session_state.df.drop(idx)
                save_data(st.session_state.df)
                st.rerun()
    else:
        st.info("ไม่พบข้อมูลแมททีเรียล")
