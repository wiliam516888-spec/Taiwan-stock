import os
import random
import requests
import pandas as pd

def send_line_message(access_token, user_id, message_text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            print("LINE 官方帳號訊息發送成功！")
        else:
            print(f"發送失敗，狀態碼：{response.status_code}，回應內容：{response.text}")
    except Exception as e:
        print(f"連線引發異常: {e}")

def main():
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    
    if not access_token or not user_id:
        print("錯誤：找不到 LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID 金鑰設定！")
        return

    print("開始執行選股策略...")
    
    # 範例選股池
    sample_stocks = [
        {"code": "6811", "name": "宏碁資訊", "price": 315.0},
        {"code": "1101", "name": "台泥", "price": 32.5},
        {"code": "2330", "name": "台積電", "price": 1020.0},
        {"code": "2317", "name": "鴻海", "price": 210.0},
        {"code": "2454", "name": "聯發科", "price": 1300.0}
    ]
    
    selected = random.sample(sample_stocks, min(3, len(sample_stocks)))
    
    # 組裝推播訊息文字
    message = "🤖 【台股每日選股精選】\n"
    message += "今日為您篩選出 3 檔實戰標的：\n"
    message += "------------------------"
    for stock in selected:
        message += f"\n📈 {stock['code']} {stock['name']}\n   參考價: {stock['price']} 元\n"
    message += "------------------------\n※ 本通知由 GitHub 雲端自動發送。"

    print("準備發送官方帳號推播...")
    send_line_message(access_token, user_id, message)

if __name__ == "__main__":
    main()
