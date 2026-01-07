import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 網頁標題與設定：旅遊助手風格
st.set_page_config(page_title="MSC 榮耀號日本航線攻略", layout="wide")
st.title("🚢 MSC 榮耀號：1/13 航線旅遊儀表板")

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

# --- 2. 核心功能：氣象數據抓取 ---
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
            # 天氣圖示邏輯
            icon = "☀️" if daily["weathercode"][i] <= 2 else "☁️" if daily["weathercode"][i] <= 3 else "🌧️"
            day_data.append(f"{min_t}°~{max_t}°C {icon}")
        weather_results[loc['name']] = day_data
    
    dates_with_week = []
    for d in daily_time:
        date_obj = datetime.strptime(d, "%Y-%m-%d")
        dates_with_week.append(f"{d[5:].replace('-', '/')}{WEEKDAYS_LIST[date_obj.weekday()]}")
    return pd.DataFrame(weather_results, index=dates_with_week).T

def color_rainy(val):
    return 'color: red' if '🌧️' in str(val) else 'color: black'

# --- 3. 顯示主區域：天氣預報 ---
df = get_weather_data()
st.subheader("🌦️ 目的地一週預報 (降雨警示)")
st.table(df.style.map(color_rainy))

# --- 4. 旅遊專屬區塊：交通、美食與必備工具 ---
st.divider()
st.subheader("🧳 日本岸上觀光指南")
col1, col2, col3 = st.columns(3)

with col1:
    with st.expander("🚌 交通接駁秘笈", expanded=True):
        st.markdown("""
        * **那霸**: 離港後建議搭 Taxi 至「旭橋站」轉單軌電車，方便前往國際通。
        * **宮古島**: 主要停靠平良港，下船後計程車較少，建議提早預約。
        * **石垣島**: 港口離市區較近，步行可至公車總站。
        """)

with col2:
    with st.expander("🍱 必吃美食清單", expanded=True):
        st.markdown("""
        * **那霸**: 阿古豬涮涮鍋、沖繩排骨麵。
        * **宮古島**: 宮古牛燒肉、雪鹽霜淇淋。
        * **石垣島**: 石垣牛漢堡、金城燒肉。
        """)

with col3:
    with st.expander("🛠️ 出國必備工具", expanded=True):
        st.write("💴 **當前匯率參考**: 1 JPY ≈ 0.215 TWD")
        st.markdown("""
        * **MSC App**: 記得登船前完成 Web Check-in
        * **網路卡**: 令和卡 eSIM 需先掃描 QR Code
        * **翻譯**: 準備好 Google Lens 拍照翻譯菜單。
        """)

# --- 5. 狀態列 ---
if days_left > 0:
    st.info(f"📅 今日：{TODAY.strftime('%Y/%m/%d')} {WEEKDAYS_LIST[TODAY.weekday()]} | 距離 **AvatarWei** 出發日 1/13 (二) 還有 **{days_left}** 天")
elif days_left == 0:
    st.success(f"🎉 啟航愉快！AvatarWei，今天就是 1/13 出發日！")
else:
    st.success("🚢 榮耀號正在航行中，享受你的日本之旅！")