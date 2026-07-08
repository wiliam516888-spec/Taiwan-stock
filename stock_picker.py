import os
import requests
import pandas as pd
from datetime import datetime

def get_real_taiwan_stock_data():
    # 使用證交所官方盤後行情 API
    url = "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df = df.rename(columns={"Code": "證券代號", "Name": "證券名稱", "ClosingPrice": "收盤價"})
            df['收盤價'] = pd.to_numeric(df['收盤價'], errors='coerce')
            return df
    except Exception as e:
        print(f"連線錯誤: {e}")
    return None

def send_line_message(access_token, user_id, message_text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": message_text}]}
    requests.post(url, json=payload, headers=headers)

def main():
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    
    df = get_real_taiwan_stock_data()
    
    if df is None or df['收盤價'].isna().all():
        print("證交所尚未提供今日收盤數據，或連線異常。")
        # 這裡不隨便給數字，確保您看到的都是真實資訊
        return

    focus_codes = ["6811", "1101", "2330", "2317", "2454"]
    df_filtered = df[df['證券代號'].isin(focus_codes)]
    
    if df_filtered.empty:
        print("今日無指定標的報價。")
        return

    message = f"🤖 【台股盤後收盤行情】({datetime.now().strftime('%Y-%m-%d')})\n------------------------"
    for _, row in df_filtered.iterrows():
        message += f"\n📈 {row['證券代號']} {row['證券名稱']}\n   收盤價: {row['收盤價']} 元\n"
    message += "\n------------------------\n※ 僅顯示當日已更新之真實數據。"

    send_line_message(access_token, user_id, message)

if __name__ == "__main__":
    main()
