import streamlit as st
import pandas as pd
import json
from streamlit_echarts import st_echarts

# --- Cấu hình Trang & Định nghĩa dữ liệu/hàm ---
st.set_page_config(
    page_title="Dashboard Khách Hàng & Doanh Thu Tour Du Lịch",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Giao diện KPI cần font 'Orbitron' - dùng HTML/Markdown an toàn
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


# Dữ liệu từ file HTML gốc (giả lập data sau khi đã tính toán)
# Chúng ta sẽ sử dụng trực tiếp các con số này để xây dựng Dashboard
DATA_PAYLOAD = {
    "kpi_total_revenue": 37860152492,
    "kpi_total_booking_value": 191033077122,
    "kpi_total_customers": 2097,
    "kpi_unique_nationalities": 17,
    "trend_chart_revenue_by_departure": [
        {"departure_date": "2025-01-01T00:00:00","total_revenue": 1059942005},{"departure_date": "2025-01-02T00:00:00","total_revenue": 8032719020},
        {"departure_date": "2025-01-03T00:00:00","total_revenue": 4418653512},{"departure_date": "2025-01-04T00:00:00","total_revenue": 6280297642},
        {"departure_date": "2025-01-05T00:00:00","total_revenue": 2387744010},{"departure_date": "2025-01-06T00:00:00","total_revenue": 1398338509},
        {"departure_date": "2025-01-07T00:00:00","total_revenue": 4039332504},{"departure_date": "2025-01-08T00:00:00","total_revenue": 1154727500},
        {"departure_date": "2025-01-09T00:00:00","total_revenue": 1090560000},{"departure_date": "2025-01-10T00:00:00","total_revenue": 3909047000},
        {"departure_date": "2025-01-11T00:00:00","total_revenue": 3216741280},{"departure_date": "2025-01-12T00:00:00","total_revenue": 78440000},
        {"departure_date": "2025-01-13T00:00:00","total_revenue": 793609510}
    ],
    "pie_gender_distribution": [{"gender": "Nam","customer_count": 872},{"gender": "Nữ","customer_count": 1225}],
    "pie_nationality_distribution": [
        {"nationality": "VN","customer_count": 1557},{"nationality": "NON","customer_count": 194},{"nationality": "USA","customer_count": 179},
        {"nationality": "AUS","customer_count": 90},{"nationality": "CA","customer_count": 28},{"nationality": "FR","customer_count": 15}
    ],
    "bar_tour_revenue": [
        {"tour_name": "Đông Bắc Á","total_revenue": 21720704941},{"tour_name": "Đông Nam Á","total_revenue": 10742389050},
        {"tour_name": "Nam Á","total_revenue": 1943540001},{"tour_name": "Tây Âu","total_revenue": 1901467000},
        {"tour_name": "Tây Á, Trung Đông, S.N.G","total_revenue": 1552051500}
    ],
    "table_detail_customer": [
        {"Họ tên": "LÊ THỊ KHUYA","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "VÕ THÀNH HIẾN","Giới tính": "Nam","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "NGUYỄN THỊ HỒNG NHUNG","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "HUỲNH THỊ MĂNG","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 101990000,"Trị giá booking": 719900000},
        {"Họ tên": "LƯU VĂN TIẾP","Giới tính": "Nam","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "LƯU LAN PHƯƠNG","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "PHẠM HOÀNG VŨ","Giới tính": "Nam","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 89990000,"Trị giá booking": 719900000},
        {"Họ tên": "CHUNG THỊ BẢY","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "CHÂU PHI TUỒNG","Giới tính": "Nam","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 66990000,"Trị giá booking": 719900000},
        {"Họ tên": "LƯƠNG NGUYỆT NGA","Giới tính": "Nữ","Quốc tịch": "VN","Tên Tour": "Tây Âu","Ngày khởi hành": "2025-01-10T00:00:00","Trị giá": 58990000,"Trị giá booking": 719900000}
    ]
}

# --- Định dạng ---
def format_kpi_value(value):
    if value >= 1e12: return f"{value / 1e12:.2f}T"
    if value >= 1e9: return f"{value / 1e9:.2f}B"
    if value >= 1e6: return f"{value / 1e6:.2f}M"
    return f"{value:,}"

def custom_kpi_card(title, value, unit='VND'):
    formatted_value = format_kpi_value(value)
    # Sử dụng HTML để kiểm soát font và màu sắc chính xác
    st.markdown(
        f"""
        <div class="kpi-title">{title}</div>
        <div class="kpi-value-container">
            {formatted_value}
            <span class="kpi-unit">{unit}</span>
        </div>
        """, unsafe_allow_html=True
    )
    # Thêm tooltip (dù không hoàn hảo như HTML gốc)
    st.caption(f"Trị giá chi tiết: {value:,.0f} VND", help=f"Tổng trị giá là: {value:,.0f} VND")


# --- Echarts Options ---
# Theme màu sắc của Echarts
ECHARTS_COLOR = ['#4A90E2', '#F5A623', '#9013FE', '#50E3C2', '#F87979', '#82D8D8', '#B7A4F9']

def get_line_chart_option(data):
    dates = [pd.to_datetime(item['departure_date']).strftime('%d/%m') for item in data]
    revenues = [item['total_revenue'] for item in data]
    
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

def get_pie_chart_option(data, label_key, value_key, title):
    data_series = [{"value": item[value_key], "name": item[label_key]} for item in data]
    
    # Tính tổng cho việc hiển thị tỷ lệ Nam/Nữ
    total_count = sum([item[value_key] for item in data])
    
    # Định dạng Legend để hiển thị số lượng
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
            "formatter": {"_custom": True, "code": legend_formatter} # Custom formatter JS
        },
        "series": [{
            "name": title, "type": 'pie', "radius": ['45%', '70%'], "center": ['70%', '50%'],
            "data": data_series,
            "label": {"show": False},
            "labelLine": {"show": False}
        }]
    }

def get_bar_chart_option(data):
    # Bar chart ngang, sort ngược lại để Top 1 nằm trên cùng
    sorted_data = sorted(data, key=lambda x: x['total_revenue'], reverse=False)
    tour_names = [item['tour_name'] for item in sorted_data]
    revenues = [item['total_revenue'] for item in sorted_data]
    
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
            "itemStyle": {"borderRadius": [0, 4, 4, 0]} # Bar ngang
        }]
    }

# --- Chạy Dashboard ---

st.title("🌌 DASHBOARD KHÁCH HÀNG & DOANH THU TOUR DU LỊCH")

# 1. KPIs
kpi_cols = st.columns(4)

with kpi_cols[0]:
    custom_kpi_card("TỔNG TRỊ GIÁ", DATA_PAYLOAD['kpi_total_revenue'])
with kpi_cols[1]:
    custom_kpi_card("TỔNG TRỊ GIÁ BOOKING", DATA_PAYLOAD['kpi_total_booking_value'])
with kpi_cols[2]:
    custom_kpi_card("TỔNG SỐ KHÁCH", DATA_PAYLOAD['kpi_total_customers'], unit='Người')
with kpi_cols[3]:
    custom_kpi_card("SỐ QUỐC TỊCH", DATA_PAYLOAD['kpi_unique_nationalities'], unit='Quốc tịch')

# 2. Biểu đồ chính
chart_row2_col1, chart_row2_col2, chart_row2_col3 = st.columns(3)

# Xu hướng Doanh Thu
with chart_row2_col1:
    st.subheader("📈 XU HƯỚNG TRỊ GIÁ THEO NGÀY KHỞI HÀNH")
    st_echarts(options=get_line_chart_option(DATA_PAYLOAD['trend_chart_revenue_by_departure']), height="350px")

# Phân Bố Giới Tính
with chart_row2_col2:
    st.subheader("👥 PHÂN BỐ GIỚI TÍNH")
    st_echarts(options=get_pie_chart_option(DATA_PAYLOAD['pie_gender_distribution'], 'gender', 'customer_count', 'Phân Bố Giới Tính'), height="350px")

# Phân Bố Quốc Tịch
with chart_row2_col3:
    st.subheader("🗺️ PHÂN BỐ QUỐC TỊCH")
    st_echarts(options=get_pie_chart_option(DATA_PAYLOAD['pie_nationality_distribution'], 'nationality', 'customer_count', 'Phân Bố Quốc Tịch'), height="350px")

# 3. Biểu đồ Bar và Chi tiết
chart_row3_col1, chart_row3_col2 = st.columns(2)

# Top Tour Doanh Thu
with chart_row3_col1:
    st.subheader("🏆 TOP 5 TOUR DOANH THU CAO NHẤT")
    st_echarts(options=get_bar_chart_option(DATA_PAYLOAD['bar_tour_revenue']), height="350px")

# Bảng Chi tiết (dùng Pandas Dataframe)
with chart_row3_col2:
    st.subheader("📑 CHI TIẾT BOOKING KHÁCH HÀNG")
    df_detail = pd.DataFrame(DATA_PAYLOAD['table_detail_customer'])
    
    # Định dạng hiển thị trong Dataframe
    df_styled = df_detail.style.format({
        'Trị giá': lambda x: f"{x:,.0f} VND",
        'Trị giá booking': lambda x: f"{x:,.0f} VND",
        'Ngày khởi hành': lambda x: pd.to_datetime(x).strftime('%d/%m/%Y')
    })
    
    st.dataframe(df_styled, height=350, use_container_width=True)
