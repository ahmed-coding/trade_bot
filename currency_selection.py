import requests
import pandas as pd
from datetime import datetime, timedelta

class CurrencySelector:
    def __init__(self, symbol, interval="1d", min_history_days=90):
        self.symbol = symbol
        self.interval = interval
        self.min_history_days = min_history_days
        self.data = None

    def fetch_currency_data(self):
        # جمع البيانات التاريخية للعملة باستخدام Binance API
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.min_history_days)
        start_time_str = int(start_time.timestamp() * 1000)
        
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "startTime": start_time_str,
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if len(data) < self.min_history_days:
            print(f"البيانات غير كافية للعملة {self.symbol}، تحتوي على {len(data)} يوم فقط.")
            return False
        
        self.data = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
        self.data["close"] = self.data["close"].astype(float)
        print(f"تم جمع البيانات التاريخية للعملة {self.symbol} لمدة {self.min_history_days} يوم")
        return True

    def is_currency_suitable(self):
        # التحقق مما إذا كانت العملة مناسبة بناءً على وجود البيانات
        sufficient_data = self.fetch_currency_data()
        if sufficient_data:
            return self.analyze_currency()
        else:
            print(f"العملة {self.symbol} تمتلك بيانات قصيرة المدى وسيتم تحليلها مؤقتًا.")
            return self.analyze_new_currency()

    def analyze_currency(self):
        # تحليل العملة بناءً على بيانات تتجاوز 3 أشهر
        trend = self.data["close"].pct_change().mean()  # تحليل بسيط للاتجاه
        volatility = self.data["close"].pct_change().std()  # حساب التذبذب
        print(f"تحليل العملة {self.symbol}، الاتجاه: {trend}, التذبذب: {volatility}")
        
        return trend > 0 and volatility < 0.05  # مثال على شروط الاختيار

    def analyze_new_currency(self):
        # تحليل سريع للعملات التي لا تتجاوز بياناتها 3 أشهر
        avg_price = self.data["close"].mean() if self.data is not None else 0
        print(f"تحليل سريع للعملة {self.symbol} بناءً على البيانات القصيرة، متوسط السعر: {avg_price}")
        
        return avg_price > 1  # مثال بسيط لشروط العملة الجديدة
