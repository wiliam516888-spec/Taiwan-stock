import os
import requests
import pandas as pd
from datetime import datetime

def get_taiwan_stock_data():
    """從公開 API 抓取台股上市股票今日個股收盤行情"""
    print("正在抓取台股盤後數據...")
    # 使用證交所每日收盤行情 API
    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUT0999"
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if "data9" not in data:
            return None
            
        # 解析個股資料
        columns = [
            "證券代號", "證券名稱", "成交股數", "成交筆數", "成交金額",
            "開盤價", "最高價", "最低價", "收盤價", "漲跌(+/-)",
            "漲跌價差", "最後揭示買價", "最後揭示買量", "最後揭示賣價",
            "最後揭示賣量", "本益比"
        ]
        df = pd.DataFrame(data["data9"], columns=columns)
        return df
    except Exception as e:
        print(f"資料抓取失敗: {e}")
        return None

def select_stocks(df):
    """基礎選股邏輯：篩選價格與成交量健康的標的"""
    if df is None or df.empty:
        return ["無法取得今日台股數據，請檢查開盤狀態。"]
        
    try:
        # 清理數據：將收盤價、成交股數轉為數字
        df["收盤價"] = df["收盤價"].str.replace(",", "").replace("--", "0")
        df["收盤價"] = pd.to_numeric(df["收盤價"], errors='coerce')
        df["成交股數"] = pd.to_numeric(df["成交股數"].str.replace(",", ""), errors='coerce')
        
        # 基礎篩選：過濾掉權證、ETF（代號非4碼或6碼純數字的），並篩選股價大於10元、成交量大於1000張（1,000,000股）的股票
        df = df[df["證券代號"].str.match(r"^\d{4}$")] # 篩選標準4碼個股
        valid_df = df[(df["收盤價"] > 10) & (df["成交股數"] > 1000000)].copy()
        
        # 簡單示範：隨機挑選 3 檔（後續可依型態學或位階法調整更嚴格的移動平均線、量價突破邏輯）
        picked = valid_df.sample(n=min(3, len(valid_df)))
        
        results = []
        for _, row in picked.iterrows():
            results.append(f"📈 股票: {row['證券代號']} {row['證券名稱']}\n   收盤價: {row['收盤價']} 元\n   成交量: {int(row['成交股數']/1000):,} 張")
            
        return results
    except Exception as e:
        return [f"選股計算過程發生錯誤: {e}"]

def send_line_notify(message):
    """發送訊息至 LINE Notify"""
    token = os.environ.get("LINE_NOTIFY_TOKEN")
    if not token:
        print("錯誤：找不到 LINE_NOTIFY_TOKEN 密鑰設定！")
        return
        
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("LINE 通知發送成功！")
    else:
        print(f"LINE 通知發送失敗，錯誤碼: {response.status_code}")

if __name__ == "__main__":
    today_str = datetime.now().strftime("%Y-%m-%d")
    msg_content = f"\n🤖 【台股每日選股助理】\n📅 日期: {today_str}\n"
    msg_content += "-------------------------\n"
    
    stock_df = get_taiwan_stock_data()
    picked_stocks = select_stocks(stock_df)
    
    for stock in picked_stocks:
        msg_content += stock + "\n"
        
    msg_content += "-------------------------\n※ 以上僅供程式範例測試，非投資建議。"
    
    # 執行發送
    send_line_notify(msg_content)
