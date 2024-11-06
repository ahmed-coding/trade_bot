import requests
import pandas as pd
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self, symbol="BTCUSDT", intervals=["1h", "4h", "1d"], min_history_days=30):
        """
        :param symbol: رمز العملة الرقمية لجلب البيانات (مثل BTCUSDT).
        :param intervals: قائمة بالأطر الزمنية المطلوبة لجمع البيانات بشكل ديناميكي.
        :param min_history_days: الحد الأدنى للأيام المطلوبة لجمع البيانات.
        """
        self.symbol = symbol
        self.intervals = intervals
        self.min_history_days = min_history_days
        self.data = {}

    def fetch_data(self):
        """جمع البيانات التاريخية للرمز المحدد عبر الأطر الزمنية المختلفة بشكل ديناميكي"""
        for interval in self.intervals:
            print(f"جلب البيانات للإطار الزمني {interval} للرمز {self.symbol}")
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=self.min_history_days)
            start_time_str = int(start_time.timestamp() * 1000)
            all_data = []

            while True:
                url = "https://api.binance.com/api/v3/klines"
                params = {
                    "symbol": self.symbol,
                    "interval": interval,
                    "startTime": start_time_str,
                    "limit": 1000  # الحد الأقصى لكل طلب
                }
                response = requests.get(url, params=params)
                data = response.json()

                if not data:
                    break

                all_data.extend(data)
                start_time_str = data[-1][0] + 1  # تحديث لـ `start_time` للطلب القادم

                # التوقف عند جمع عدد كافٍ من البيانات
                if len(all_data) >= self.min_required_points(interval):
                    break

            # التحقق من توافر البيانات بشكل كافٍ وإضافتها
            if len(all_data) < self.min_required_points(interval):
                print(f"البيانات غير كافية للرمز {self.symbol} للإطار {interval}")
                self.data[interval] = None
            else:
                df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume", 
                                                     "close_time", "quote_asset_volume", "number_of_trades", 
                                                     "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", 
                                                     "ignore"])
                df["close"] = df["close"].astype(float)
                self.data[interval] = df
                print(f"تم جمع البيانات للإطار {interval} بنجاح.")

    def min_required_points(self, interval):
        """حساب العدد الأدنى من النقاط المطلوبة استنادًا إلى الإطار الزمني"""
        points_per_day = 24 if interval == "1h" else 6 if interval == "4h" else 1
        return int(self.min_history_days * points_per_day * 0.8)  # 80% كحد أدنى للمرونة

    def get_data(self):
        """إرجاع جميع البيانات المجمعة لكل إطار زمني"""
        return self.data

    def get_close_prices(self, interval):
        """إرجاع أسعار الإغلاق للإطار المحدد"""
        return self.data[interval]["close"].tolist() if self.data.get(interval) is not None else []
