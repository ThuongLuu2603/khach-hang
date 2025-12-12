import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# --- Cấu hình Trang ---
st.set_page_config(
    page_title="Dashboard Khách Hàng & Doanh Thu Tour Du Lịch",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Định nghĩa Hàm Tải và Xử Lý Dữ Liệu (Quan trọng) ---

# Giả lập dữ liệu thô từ Google Sheet
# THAY THẾ HÀM NÀY BẰNG HÀM KẾT NỐI VÀ TẢI DỮ LIỆU THẬT SỰ TỪ GOOGLE SHEET CỦA BẠN.
# Ví dụ: Dùng st.connection("gsheets") hoặc đọc link public CSV/Excel
def load_and_transform_data():
    # Giả lập dữ liệu thô tương tự như từ Google Sheet
    # Cột: Họ tên, Giới tính, Quốc tịch, Tên Tour, Ngày khởi hành, Trị giá, Trị giá booking
    
    # Dữ liệu mẫu (chỉ để minh họa, dựa trên payload bạn cung cấp)
    raw_data_json = """[
        {"Họ tên": "LÊ THỊ KHUYA","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "VÕ THÀNH HIẾN","Giới tính": "Nam","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "NGUYỄN THỊ HỒNG NHUNG","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "HUỲNH THỊ MĂNG","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 101990000,"Trị giá booking": 719900000},
        {"Họ tên": "LƯU VĂN TIẾP","Giới tính": "Nam","Quốc tịch": "VN","Tên Tour": "Đông Nam Á","Ngày khởi hành": "2025-01-02T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "LƯU LAN PHƯƠNG","Giới tính": "Nữ","Quốc tịch": "NON","Tên Tour": "Đông Nam Á","Ngày khởi hành": "2025-01-02T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "PHẠM HOÀNG VŨ","Giới tính": "Nam","Quốc tịch": "USA","Tên Tour": "Đông Bắc Á","Ngày khởi hành": "2025-01-01T00:00:00","Trị giá": 89990000,"Trị giá booking": 719900000},
        {"Họ tên": "CHUNG THỊ BẢY","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Đông Bắc Á","Ngày khởi hành": "2025-01-01T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "CHÂU PHI TUỒNG","Giới tính": "Nam","Quốc tịch": "VN","Tên Tour": "Đông Bắc Á","Ngày khởi hành": "2025-01-01T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "LƯƠNG NGUYỆT NGA","Giới tính": "Nữ","Quốc tịch": "USA","Tên Tour": "Đông Bắc Á","Ngày khởi hành": "2025-01-01T00:00:00","Trị giá": 58990000,"Trị giá booking": 719900000},
        {"Họ tên": "VĂN THANH HẢI","Giới tính": "Nam","Quốc tịch": "AUS","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 90000000,"Trị giá booking": 719900000},
        {"Họ tên": "TRẦN VĂN AN","Giới tính": "Nam","Quốc tịch": "AUS","Tên Tour": "Đông Nam Á","Ngày khởi hành": "2025-01-03T00:00:00","Trị giá": 70000000,"Trị giá booking": 719900000},
        {"Họ tên": "PHAN THỊ HOA","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Đông Bắc Á","Ngày khởi hành": "2025-01-04T00:00:00","Trị giá": 120000000,"Trị giá booking": 719900000}
    ]"""
    df_raw = pd.DataFrame(json.loads(raw_data_json))
    
    # 1. Chuyển đổi kiểu dữ liệu
    df_raw['Trị giá'] = pd.to_numeric(df_raw['Trị giá'], errors='coerce')
    df_raw['Trị giá booking'] = pd.to_numeric(df_raw['Trị giá booking'], errors='coerce')
    df_raw['Ngày khởi hành'] = pd.to_datetime(df_raw['Ngày khởi hành'])
    
    # 2. Tính toán cho KPI
    total_revenue = df_raw['Trị giá'].sum()
    total_booking_value = df_raw['Trị giá booking'].sum()
    total_customers = df_raw.shape[0] # Giả định mỗi dòng là 1 khách
    unique_nationalities = df_raw['Quốc tịch'].nunique()
    
    kpis = {
        "Tổng Trị Giá": total_revenue,
        "Tổng Trị Giá Booking": total_booking_value,
        "Tổng Số Khách": total_customers,
        "Số Quốc Tịch": unique_nationalities
    }
    
    # 3. Tính toán cho Biểu đồ
    # Xu hướng Doanh Thu
    df_trend = df_raw.groupby(df_raw['Ngày khởi hành'].dt.date)['Trị giá'].sum().reset_index()
    df_trend.columns = ['departure_date', 'total_revenue']
    
    # Phân bố Giới tính
    df_gender = df_raw.groupby('Giới tính').size().reset_index(name='customer_count')
    
    # Phân bố Quốc tịch (Top N)
    df_nationality = df_raw.groupby('Quốc tịch').size().reset_index(name='customer_count').sort_values('customer_count', ascending=False).head(6)
    
    # Tour Doanh Thu Cao Nhất (Top 5)
    df_tour_revenue = df_raw.groupby('Tên Tour')['Trị giá'].sum().reset_index(name='total_revenue').sort_values('total_revenue', ascending=False).head(5)
    
    return kpis, df_trend, df_gender, df_nationality, df_tour_revenue, df_raw

# Định dạng tiền tệ
def format_currency(value):
    if abs(value) >= 1e9:
        return f"{value / 1e9:.2f} B VND"
    elif abs(value) >= 1e6:
        return f"{value / 1e6:.2f} M VND"
    return f"{value:,.0f} VND"

# Định dạng số lớn
def format_number(value):
    return f"{value:,.0f}"

# --- Giao diện Streamlit ---

st.title("🌌 Dashboard Khách Hàng & Doanh Thu Tour Du Lịch")
st.markdown("Cập nhật dữ liệu từ **Google Sheet** (Giả lập) và trực quan hóa bằng **Streamlit/Plotly**.")
st.markdown("---")

# Tải và xử lý dữ liệu
kpis, df_trend, df_gender, df_nationality, df_tour_revenue, df_detail = load_and_transform_data()

# 1. Hiển thị KPI
st.header("✨ Chỉ Số Hiệu Suất Chính (KPIs)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Tổng Trị Giá", format_currency(kpis['Tổng Trị Giá']))
with col2:
    st.metric("Tổng Trị Giá Booking", format_currency(kpis['Tổng Trị Giá Booking']))
with col3:
    st.metric("Tổng Số Khách", format_number(kpis['Tổng Số Khách']))
with col4:
    st.metric("Số Quốc Tịch", format_number(kpis['Số Quốc Tịch']))

st.markdown("---")

# 2. Hiển thị Biểu đồ
st.header("📊 Phân Tích Chi Tiết")
chart_col1, chart_col2 = st.columns([7, 5])

# Biểu đồ 1: Xu hướng Doanh Thu Theo Ngày Khởi Hành (Line Chart)
with chart_col1:
    st.subheader("📈 Xu Hướng Trị Giá Theo Ngày Khởi Hành")
    fig_line = px.line(df_trend, x='departure_date', y='total_revenue', 
                       title='Trị Giá Thu Nhập Theo Ngày',
                       labels={'departure_date': 'Ngày Khởi Hành', 'total_revenue': 'Trị Giá (VND)'},
                       markers=True)
    fig_line.update_layout(yaxis_tickformat='.2s') # Định dạng trục Y
    st.plotly_chart(fig_line, use_container_width=True)

# Biểu đồ 2 & 3: Phân Bố Giới Tính và Quốc Tịch (Pie Charts)
with chart_col2:
    tab_gender, tab_nationality = st.tabs(["Phân Bố Giới Tính", "Phân Bố Quốc Tịch"])
    
    with tab_gender:
        fig_gender = px.pie(df_gender, values='customer_count', names='Giới tính', 
                            title='Phân Bố Giới Tính Khách Hàng', hole=.3)
        st.plotly_chart(fig_gender, use_container_width=True)
        
    with tab_nationality:
        fig_nationality = px.pie(df_nationality, values='customer_count', names='Quốc tịch', 
                                title='Phân Bố Quốc Tịch (Top 6)', hole=.3)
        st.plotly_chart(fig_nationality, use_container_width=True)

st.markdown("---")

# Biểu đồ 4: Top Tour Doanh Thu (Bar Chart)
st.subheader("💰 Top 5 Tour Doanh Thu Cao Nhất")
fig_bar = px.bar(df_tour_revenue.sort_values('total_revenue', ascending=True), 
                 x='total_revenue', y='Tên Tour', 
                 orientation='h',
                 title='Doanh Thu Của Từng Tour',
                 labels={'Tên Tour': 'Tên Tour', 'total_revenue': 'Trị Giá (VND)'})
fig_bar.update_layout(xaxis_tickformat='.2s')
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 3. Bảng Chi tiết
st.header("📑 Chi Tiết Booking Khách Hàng (10 dòng đầu)")
st.dataframe(df_detail.head(10).style.format({
    'Trị giá': lambda x: f"{x:,.0f} VND",
    'Trị giá booking': lambda x: f"{x:,.0f} VND",
    'Ngày khởi hành': lambda x: x.strftime('%d/%m/%Y')
}), use_container_width=True)
