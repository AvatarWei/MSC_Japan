import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 網頁配置
st.set_page_config(page_title="MSC 航線旅遊助手", layout="wide")

# --- 1. 定義全域變數 ---
WEEKDAYS_LIST = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]
DEPARTURE_DATE = datetime(2026, 1, 13)
TODAY = datetime.now()
days_left = (DEPARTURE_DATE.date() - TODAY.date()).days

locations = [
    {"name": "那霸 (Naha)", "lat": 26.21, "lon": 127.68},
    {"name": "宮古島 (Miyako)", "lat": 24.80, "lon": 125.28},
    {"name": "石垣島 (Ishigaki)", "lat": 24.34, "lon": 124.15}
]

# --- 2. 新增：即時匯率抓取函式 ---
def get_jpy_rate():
    try:
        # 使用免 Key 的 Open-Meteo 同體系或免費匯率 API
        url = "https://open.er-api.com/v6/latest/TWD"
        res = requests.get(url).json()
        # 計算 1 JPY 等於多少 TWD (TWD / JPY)
        jpy_in_twd = 1 / res["rates"]["JPY"]
        return round(jpy_in_twd, 4)
    except:
        return 0.215  # 若 API 失效，回傳預設值

# --- 3. 氣象數據抓取 ---
def get_weather_data():
    weather_results = {}
    daily_time = [] 
    for loc in locations:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['lat']}&longitude={loc['lon']}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo"
        res = requests.get(url).json()
        daily = res["daily"]
        daily_time = daily["time"]
        day_data = []
        for i in range(7):
            max_t, min_t = int(daily['temperature_2m_max'][i]), int(daily['temperature_2m_min'][i])
            icon = "☀️" if daily["weathercode"][i] <= 2 else "☁️" if daily["weathercode"][i] <= 3 else "🌧️"
            day_data.append(f"{min_t}°~{max_t}°C {icon}")
        weather_results[loc['name']] = day_data
    
    dates_with_week = [f"{d[5:].replace('-', '/')}{WEEKDAYS_LIST[datetime.strptime(d, '%Y-%m-%d').weekday()]}" for d in daily_time]
    return pd.DataFrame(weather_results, index=dates_with_week).T

# --- 4. 顯示與風格 ---
st.title("🚢 MSC 榮耀號：1/13 航線旅遊儀表板")
df = get_weather_data()
current_rate = get_jpy_rate()

st.subheader("🌦️ 目的地一週預報 (降雨警示)")
st.table(df.style.map(lambda x: 'color: red; font-weight: bold' if '🌧️' in str(x) else 'color: black'))

st.divider()
st.subheader("🧳 日本岸上觀光懶人包")
col1, col2, col3 = st.columns(3)

with col1:
    with st.expander("🚌 交通接駁秘笈", expanded=True):
        st.markdown(f"* **那霸 (1/13)**: 建議搭 Taxi 至旭橋站\n* **宮古島 (1/15)**: 停靠平良港需預約車\n* **石垣島 (1/16)**: 總站搭川平線")

with col2:
    with st.expander("🍱 必吃美食清單", expanded=True):
        st.markdown(f"* **那霸**: 阿古豬\n* **宮古**: 宮古牛燒肉\n* **石垣**: 石垣牛漢堡")

with col3:
    with st.expander("⚙️ 即時系統參數", expanded=True):
        # 動態顯示匯率
        st.write(f"💴 **即時日幣匯率**: 1 JPY ≈ **{current_rate}** TWD")
        st.markdown(f"* **網卡**: eSIM 令和卡\n* **App**: MSC for Me")

# --- 5. 狀態列 ---
st.info(f"📅 今日日期：{TODAY.strftime('%Y/%m/%d')} | 距離 **AvatarWei** 出發日 1/13 (二) 還有 **{days_left}** 天")
