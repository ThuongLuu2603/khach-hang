import streamlit as st
import pandas as pd
import json
from streamlit_echarts import st_echarts
from datetime import datetime
import streamlit_gsheets as gs

# --- Cấu hình Trang & Custom CSS (Giữ nguyên giao diện Sci-Fi) ---
# (Phần CSS và cấu hình ECharts vẫn được giữ nguyên để đảm bảo giao diện)

st.set_page_config(
    page_title="Dashboard Khách Hàng & Doanh Thu Tour Du Lịch",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện KPI và font Orbitron (giữ nguyên từ câu trả lời trước)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
.kpi-title {
    font-size: 1rem;
    color: #E0E0E0;
    margin-top: 5px;
    font-family: 'Orbitron', sans-serif;
    text-align: center;
}
.kpi-value-container {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: #E0E0E0;
    text-shadow: 0 0 8px #F5A623;
    display: flex;
    align-items: center;
    justify-content: center;
}
.kpi-unit {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.0rem;
    font-weight: 700;
    color: #F5A623;
    margin-left: 8px;
}
.stMetric {
    background-color: rgba(17, 24, 39, 0.8);
    border: 1px solid rgba(59, 130, 246, 0.5);
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# --- HÀM TẢI VÀ XỬ LÝ DỮ LIỆU THỰC TỪ GOOGLE SHEET ---
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1DTGmU-88bPkTXVqnx8yyXsN29XJ1yxIY/export?format=csv&gid=1963553554"
@st.cache_data(ttl=600) # Cache dữ liệu 10 phút
def load_data_from_gsheets():
    try:
        # Đọc dữ liệu trực tiếp từ link CSV
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
        
        # Loại bỏ các dòng hoàn toàn trống
        df.dropna(how='all', inplace=True)
        
        # Đặt lại tên cột cho dễ xử lý và ánh xạ theo thứ tự (dựa trên ảnh Google Sheet)
        df.columns = [
            'STT', 'Mã Tour', 'Tên Tour', 'Ngày Khởi Hành', 'Mã Duy Nhất',
            'Họ Tên', 'Ngày Sinh', 'Giới Tính', 'Email', 'Di Động',
            'Passport', 'Email Khác', 'Ghi Chú', 'Quốc Tịch', 'Trị Giá',
            'Trị Giá Booking', 'Số Lượng Khách'
        ]

        # 1. Chuyển đổi kiểu dữ liệu (Giữ nguyên logic làm sạch tiền tệ)
        def clean_currency(value):
            if isinstance(value, str):
                # Loại bỏ ký tự VNĐ, dấu phân cách hàng nghìn (.), dấu thập phân (,)
                return value.replace(' VND', '').replace('.', '').replace(',', '').strip()
            return value

        df['Trị Giá'] = pd.to_numeric(df['Trị Giá'].apply(clean_currency), errors='coerce')
        df['Trị Giá Booking'] = pd.to_numeric(df['Trị Giá Booking'].apply(clean_currency), errors='coerce')
        
        # Định dạng ngày tháng: Cột 'Ngày Khởi Hành' trong sheet là 'dd/mm/yyyy'
        df['Ngày Khởi Hành'] = pd.to_datetime(df['Ngày Khởi Hành'], errors='coerce', format='%d/%m/%Y')
        
        # Làm sạch cột số lượng khách (để lấy số)
        df['Số Lượng Khách'] = pd.to_numeric(df['Số Lượng Khách'].apply(lambda x: x.split()[0] if isinstance(x, str) and x else x), errors='coerce')
        df['Số Lượng Khách'].fillna(1, inplace=True)
        
        return df
        
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu từ Google Sheet: {e}. Vui lòng kiểm tra lại link CSV và định dạng cột.")
        return pd.DataFrame()

# --- Định dạng và Echarts Options (Giữ nguyên) ---

def format_kpi_value(value):
    if value >= 1e12: return f"{value / 1e12:.2f}T"
    if value >= 1e9: return f"{value / 1e9:.2f}B"
    if value >= 1e6: return f"{value / 1e6:.2f}M"
    return f"{int(value):,}" if value is not None else "0"

def custom_kpi_card(title, value, unit='VND'):
    formatted_value = format_kpi_value(value)
    st.markdown(
        f"""
        <div class="kpi-title">{title}</div>
        <div class="kpi-value-container">
            {formatted_value}
            <span class="kpi-unit">{unit}</span>
        </div>
        """, unsafe_allow_html=True
    )
    st.caption(f"Trị giá chi tiết: {value:,.0f} {unit}" if value is not None else "Không có dữ liệu", 
               help=f"Tổng trị giá là: {value:,.0f} {unit}")

# Echarts Theme
ECHARTS_COLOR = ['#4A90E2', '#F5A623', '#9013FE', '#50E3C2', '#F87979', '#82D8D8', '#B7A4F9', '#BD10E0']

def get_line_chart_option(df):
    df_agg = df.groupby(df['Ngày Khởi Hành'].dt.date)['Trị Giá'].sum().reset_index()
    df_agg.columns = ['departure_date', 'total_revenue']
    df_agg.dropna(inplace=True)
    
    dates = [pd.to_datetime(item).strftime('%d/%m/%Y') for item in df_agg['departure_date']]
    revenues = df_agg['total_revenue'].tolist()
    
    return {
        "grid": {"top": '15%', "right": '5%', "bottom": '20%', "left": '15%'},
        "color": [ECHARTS_COLOR[0]],
        "tooltip": {"trigger": 'axis', "axisPointer": {"type": 'cross'}, "formatter": "Ngày: {b}<br/>Doanh thu: <strong>{c:,.0f} VND</strong>"},
        "xAxis": {
            "type": 'category', "boundaryGap": False, "data": dates,
            "axisLine": {"lineStyle": {"color": 'rgba(224, 224, 224, 0.3)'}},
            "axisLabel": {"rotate": 30, "color": 'rgba(224, 224, 224, 0.7)'}
        },
        "yAxis": {
            "type": 'value', 
            "axisLabel": {"formatter": "${value} B".replace('$', format_kpi_value)},
            "splitLine": {"lineStyle": {"color": 'rgba(224, 224, 224, 0.15)', "type": 'dashed'}}
        },
        "series": [{
            "name": 'Xu Hướng Trị Giá', "type": 'line', "smooth": True, "symbol": 'circle', "symbolSize": 6,
            "data": revenues,
            "areaStyle": {
                "color": {"type": 'linear', "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [{"offset": 0, "color": '#4A90E2'}, {"offset": 1, "color": 'rgba(74, 144, 226, 0)'}]
                }
            }
        }]
    }

def get_pie_chart_option(df, label_key, value_key, title):
    df_agg = df.groupby(label_key)[value_key].sum().reset_index(name='count')
    df_agg.dropna(inplace=True)
    
    data_series = [{"value": item['count'], "name": item[label_key]} for index, item in df_agg.iterrows()]
    total_count = df_agg['count'].sum()
    
    # Custom formatter JS để hiển thị giá trị và phần trăm
    legend_formatter = """function (name) {
        var value = 0;
        var percent = 0;
        var data = """ + json.dumps(data_series) + """;
        var total = """ + str(total_count) + """;
        for (var i = 0; i < data.length; i++) {
            if (data[i].name == name) {
                value = data[i].value;
                percent = (value / total * 100).toFixed(1);
            }
        }
        return name + ': ' + value + ' (' + percent + '%)';
    }"""
    
    return {
        "color": ECHARTS_COLOR,
        "tooltip": {"trigger": 'item', "formatter": '{b}: {c} ({d}%)'},
        "legend": {
            "orient": 'vertical', "left": 'left', "top": 'center',
            "textStyle": {"color": '#E0E0E0'},
            "formatter": {"_custom": True, "code": legend_formatter}
        },
        "series": [{
            "name": title, "type": 'pie', "radius": ['45%', '70%'], "center": ['70%', '50%'],
            "data": data_series,
            "label": {"show": False},
            "labelLine": {"show": False}
        }]
    }

def get_bar_chart_option(df):
    # Tính tổng doanh thu theo Tour, lấy top 5
    df_agg = df.groupby('Tên Tour')['Trị Giá'].sum().reset_index(name='total_revenue')
    df_agg = df_agg.sort_values('total_revenue', ascending=False).head(5)
    
    # Bar chart ngang, sort ngược lại để Top 1 nằm trên cùng
    sorted_data = df_agg.sort_values('total_revenue', ascending=True)
    tour_names = sorted_data['Tên Tour'].tolist()
    revenues = sorted_data['total_revenue'].tolist()
    
    return {
        "grid": {"top": '5%', "right": '5%', "bottom": '5%', "left": '30%'},
        "color": [ECHARTS_COLOR[0]],
        "tooltip": {"trigger": 'axis', "axisPointer": {"type": 'shadow'}, "formatter": "{b}<br/>Doanh thu: <strong>{c:,.0f} VND</strong>"},
        "xAxis": {
            "type": 'value', 
            "axisLabel": {"formatter": "${value} B".replace('$', format_kpi_value)},
            "splitLine": {"lineStyle": {"color": 'rgba(224, 224, 224, 0.15)', "type": 'dashed'}}
        },
        "yAxis": {
            "type": 'category', "data": tour_names,
            "axisLine": {"lineStyle": {"color": 'rgba(224, 224, 224, 0.3)'}},
            "axisLabel": {"color": 'rgba(224, 224, 224, 0.7)'}
        },
        "series": [{
            "name": 'Doanh Thu', "type": 'bar',
            "data": revenues,
            "itemStyle": {"borderRadius": [0, 4, 4, 0]}
        }]
    }

# --- Chạy Dashboard ---
st.title("🌌 DASHBOARD KHÁCH HÀNG & DOANH THU TOUR DU LỊCH")

# Tải dữ liệu thật
df_data = load_data_from_gsheets()

if not df_data.empty:
    # 1. TÍNH TOÁN KPIs
    total_revenue = df_data['Trị Giá'].sum()
    total_booking_value = df_data['Trị Giá Booking'].sum()
    total_customers = df_data['Số Lượng Khách'].sum()
    unique_nationalities = df_data['Quốc Tịch'].nunique()
    
    kpi_cols = st.columns(4)

    with kpi_cols[0]:
        custom_kpi_card("TỔNG TRỊ GIÁ", total_revenue)
    with kpi_cols[1]:
        custom_kpi_card("TỔNG TRỊ GIÁ BOOKING", total_booking_value)
    with kpi_cols[2]:
        custom_kpi_card("TỔNG SỐ KHÁCH", total_customers, unit='Người')
    with kpi_cols[3]:
        custom_kpi_card("SỐ QUỐC TỊCH", unique_nationalities, unit='Quốc tịch')

    # 2. BIỂU ĐỒ CHÍNH
    st.markdown("---")
    chart_row2_col1, chart_row2_col2, chart_row2_col3 = st.columns(3)

    # Xu hướng Doanh Thu
    with chart_row2_col1:
        st.subheader("📈 XU HƯỚNG TRỊ GIÁ THEO NGÀY KHỞI HÀNH")
        st_echarts(options=get_line_chart_option(df_data), height="350px")

    # Phân Bố Giới Tính
    with chart_row2_col2:
        st.subheader("👥 PHÂN BỐ GIỚI TÍNH")
        # Phân bố theo số lượng khách, không phải số dòng (nếu cột Số Lượng Khách > 1)
        st_echarts(options=get_pie_chart_option(df_data, 'Giới Tính', 'Số Lượng Khách', 'Phân Bố Giới Tính'), height="350px")

    # Phân Bố Quốc Tịch
    with chart_row2_col3:
        st.subheader("🗺️ PHÂN BỐ QUỐC TỊCH")
        st_echarts(options=get_pie_chart_option(df_data, 'Quốc Tịch', 'Số Lượng Khách', 'Phân Bố Quốc Tịch'), height="350px")

    # 3. Biểu đồ Bar và Chi tiết
    st.markdown("---")
    chart_row3_col1, chart_row3_col2 = st.columns(2)

    # Top Tour Doanh Thu
    with chart_row3_col1:
        st.subheader("🏆 TOP 5 TOUR DOANH THU CAO NHẤT")
        st_echarts(options=get_bar_chart_option(df_data), height="350px")

    # Bảng Chi tiết
    with chart_row3_col2:
        st.subheader("📑 CHI TIẾT BOOKING KHÁCH HÀNG (10 dòng đầu)")
        # Chọn các cột hiển thị theo yêu cầu trong ảnh:
        df_display = df_data[['Họ Tên', 'Giới Tính', 'Quốc Tịch', 'Tên Tour', 'Ngày Khởi Hành', 'Trị Giá', 'Trị Giá Booking']].head(10)
        
        # Định dạng hiển thị trong Dataframe
        df_styled = df_display.style.format({
            'Trị Giá': lambda x: f"{x:,.0f} VND" if pd.notna(x) else "",
            'Trị Giá Booking': lambda x: f"{x:,.0f} VND" if pd.notna(x) else "",
            'Ngày Khởi Hành': lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else ""
        })
        
        st.dataframe(df_styled, height=350, use_container_width=True)

else:
    st.warning("Không thể tải dữ liệu từ Google Sheet hoặc dữ liệu trống sau khi làm sạch.")
