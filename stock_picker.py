import os
import requests
import pandas as pd
from datetime import datetime

def get_real_taiwan_stock_data():
    """直接對接證交所每日下午 16:00 前必更新的大盤總報表 (MI_INDEX)"""
    print("正在連線證交所每日即時盤後總報表...")
    
    # 這是證交所每日盤後最核心、最即時的數據網址
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUT0999&_={int(datetime.now().timestamp())}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            json_data = response.json()
            if "data9" in json_data:
                # data9 包含了當日全市場股票的代號、名稱與收盤價
                df = pd.DataFrame(json_data["data9"], columns=json_data["fields9"])
                df['證券代號'] = df['證券代號'].str.strip()
                df['證券名稱'] = df['證券名稱'].str.strip()
                
                # 清理價格字串並轉為數字
                def clean_price(x):
                    try:
                        return float(str(x).replace(',', ''))
                    except:
                        return None
                
                df['收盤價'] = df['收盤價'].apply(clean_price)
                return df
    except Exception as e:
        print(f"證交所即時總報表連線失敗: {e}")
    return None

def send_line_message(access_token, user_id, message_text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message_text}]
    }
    try:
        requests.post(url, json=payload, headers=headers, timeout=15)
    except Exception as e:
        print(f"LINE 發送異常: {e}")

def main():
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    
    # 抓取市場真實總報表
    df = get_real_taiwan_stock_data()
    
    if df is None or df.empty:
        print("今日即時總報表尚未上架或讀取失敗。")
        return

    # 您關注的核心觀察個股清單
    focus_codes = ["6811", "1101", "2330", "2317", "2454"]
    df_filtered = df[df['證券代號'].isin(focus_codes)]
    
    if df_filtered.empty:
        print("報表中找不到指定的核心個股。")
        return

    # 組裝百分之百真實的價格訊息
    message = f"🤖 【台股盤後收盤行情】\n今日（{datetime.now().strftime('%Y-%m-%d')}）最新真實收盤價：\n------------------------"
    for _, row in df_filtered.iterrows():
        price_val = row['收盤價']
        price_str = f"{price_val} 元" if price_val is not None else "今日未成交"
        message += f"\n📈 {row['證券代號']} {row['證券名稱']}\n   收盤價: {price_str}\n"
    message += "------------------------\n※ 本通知數據同步台灣證交所盤後總報表。"

    print("發送今日真實收盤價通知...")
    send_line_message(access_token, user_id, message)

if __name__ == "__main__":
    main()
