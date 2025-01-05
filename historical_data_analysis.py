import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategies.fibonacci_strategy_ai import FibonacciStrategyAI
# استيراد بقية الاستراتيجيات هنا

# class HistoricalDataAnalyzer:
#     def __init__(self, symbol="BTCUSDT", interval="1d", years=3):
#         self.symbol = symbol
#         self.interval = interval
#         self.years = years
#         self.data = None
#         self.strategies = {
#             "Fibonacci": FibonacciStrategyAI,
#             # أضف بقية الاستراتيجيات هنا
#         }

#     def fetch_historical_data(self):
#         # يجمع البيانات التاريخية لمدة 3 سنوات باستخدام Binance API
#         end_time = datetime.utcnow()
#         start_time = end_time - timedelta(days=self.years * 365)
#         start_time_str = int(start_time.timestamp() * 1000)
        
#         url = "https://api.binance.com/api/v3/klines"
#         params = {
#             "symbol": self.symbol,
#             "interval": self.interval,
#             "startTime": start_time_str,
#         }
#         response = requests.get(url, params=params)
#         data = response.json()
#         self.data = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
#         self.data["close"] = self.data["close"].astype(float)
#         print(f"تم جمع البيانات التاريخية بنجاح لآخر {self.years} سنوات")

#     def train_strategies(self):
#         # تدريب النماذج على البيانات التاريخية
#         historical_prices = self.data["close"].tolist()
#         for strategy_name, strategy_class in self.strategies.items():
#             strategy = strategy_class(historical_prices)
#             strategy.update_strategy(historical_prices)  # التدريب الأولي
#             print(f"تم تدريب نموذج {strategy_name} باستخدام بيانات تاريخية")
import requests
import pandas as pd
from datetime import datetime, timedelta

class HistoricalDataAnalyzer:
    def __init__(self, symbol="BTCUSDT", intervals=["1h", "4h", "1d"], min_history_days=30):
        self.symbol = symbol
        self.intervals = intervals
        self.min_history_days = min_history_days
        self.data = {}

    def fetch_historical_data(self):
        """جمع البيانات التاريخية للرمز المحدد عبر عدة أطر زمنية"""
        for interval in self.intervals:
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
                    "limit": 1000
                }
                response = requests.get(url, params=params)
                data = response.json()

                if not data:
                    break

                all_data.extend(data)
                start_time_str = data[-1][0] + 1

                if len(all_data) >= self.min_history_days * 24:
                    break

            # تحديد الحد الأدنى للبيانات المطلوبة بناءً على الإطار الزمني
            required_points = self.min_history_days * (24 if interval == "1h" else (6 if interval == "4h" else 1)) * 0.8
            if len(all_data) < required_points:
                print(f"البيانات غير كافية للرمز {self.symbol} للإطار {interval}")
                self.data[interval] = None
            else:
                df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume", 
                                                     "close_time", "quote_asset_volume", "number_of_trades", 
                                                     "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", 
                                                     "ignore"])
                df["close"] = df["close"].astype(float)
                self.data[interval] = df
                print(f"تم جمع البيانات التاريخية للإطار {interval} بنجاح.")
    
    def get_data_for_training(self):
        """إرجاع البيانات لجميع الأطر الزمنية الصالحة للاستخدام في التدريب"""
        return {interval: df for interval, df in self.data.items() if df is not None}

    def get_close_prices(self, interval):
        """إرجاع أسعار الإغلاق للإطار المحدد إذا كانت البيانات متوفرة"""
        return self.data[interval]["close"].tolist() if self.data.get(interval) is not None else []


    def get_trad_close_prices(self, client,symbol, limit, interval):
        """إرجاع أسعار الإغلاق للإطار المحدد إذا كانت البيانات متوفرة"""
        
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        closing_prices = [float(kline[4]) for kline in klines]
            
        return closing_prices


class NewCurrencyAnalyzer:
    def __init__(self, data, strategies):
        self.data = data
        self.strategies = strategies

    def analyze_new_currency(self):
        # إذا كانت البيانات قصيرة (أقل من 3 أشهر)، يتم تحليل السوق باستخدام استراتيجيات فورية
        for strategy_name, strategy_class in self.strategies.items():
            strategy = strategy_class(self.data)
            if strategy.should_enter_trade():
                print(f"إشارة تداول للعملة الجديدة بناءً على {strategy_name}")
