import os
import random
import requests
import pandas as pd
from datetime import datetime

def get_real_taiwan_stock_data():
    """真正從證交所 API 抓取今日全台股盤後數據"""
    print("正在連線台灣證交所獲取今日真實盤後數據...")
    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUT0999&_=" + str(int(datetime.now().timestamp()))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return None
            
        data = response.json()
        if "data9" not in data:
            return None
            
        # 解析證交所個股資料 (data9 是上市股票)
        columns = data["fields9"]
        df = pd.DataFrame(data["data9"], columns=columns)
        
        # 清理並篩選個股
        df['證券代號'] = df['證券代號'].str.strip()
        df['證券名稱'] = df['證券名稱'].str.strip()
        
        # 轉換收盤價為數字
        def clean_price(x):
            try:
                return float(x.replace(',', ''))
            except:
                return 0.0
                
        df['收盤價'] = df['收盤價'].apply(clean_price)
        return df
    except Exception as e:
        print(f"抓取證交所數據失敗: {e}")
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
    
    if not access_token or not user_id:
        print("錯誤：找不到 LINE 金鑰設定！")
        return

    # 1. 抓取今日真實數據
    df_market = get_real_taiwan_stock_data()
    
    # 您關注的核心觀察個股清單
    focus_codes = ["6811", "1101", "2330", "2317", "2454"]
    result_stocks = []

    if df_market is not None and not df_market.empty:
        # 從市場真實數據中抽取出您關注的股票當日真實收盤價
        df_filtered = df_market[df_market['證券代號'].isin(focus_codes)]
        for _, row in df_filtered.iterrows():
            result_stocks.append({
                "code": row['證券代號'],
                "name": row['證券名稱'],
                "price": row['收盤價']
            })
            
    # 備用機制：如果今天非交易日或證交所塞車，才用基本市價提示
    if not result_stocks:
        print("無法取得今日即時盤後數據，可能非交易日。")
        return

    # 隨機挑選 3 檔發送
    selected = random.sample(result_stocks, min(3, len(result_stocks)))
    
    # 2. 組裝真實價格訊息
    message = "🤖 【台股每日選股精選】\n"
    message += f"今日（{datetime.now().strftime('%Y-%m-%d')}）盤後真實行情：\n"
    message += "------------------------"
    for stock in selected:
        message += f"\n📈 {stock['code']} {stock['name']}\n   今日收盤價: {stock['price']} 元\n"
    message += "------------------------\n※ 本通知數據同步台灣證交所。"

    print("準備發送真實行情通知...")
    send_line_message(access_token, user_id, message)

if __name__ == "__main__":
    main()
