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
    def __init__(self, symbol="BTCUSDT", interval="1h", years=3):
        self.symbol = symbol
        self.interval = interval
        self.years = years
        self.data = pd.DataFrame()

    def fetch_historical_data(self):
        """جمع البيانات التاريخية على فترات باستخدام Binance API"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.years * 365)
        start_time_str = int(start_time.timestamp() * 1000)
        
        while True:
            # إعداد طلب API لجلب البيانات من فترة معينة
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": self.symbol,
                "interval": self.interval,
                "startTime": start_time_str,
                "limit": 1000  # الحد الأقصى لكل طلب (1000 نقطة بيانات)
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if not data:
                # إذا لم يكن هناك بيانات جديدة، يتم التوقف عن التحميل
                break
            
            # تحويل البيانات إلى DataFrame وإضافتها إلى البيانات الرئيسية
            temp_df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
            temp_df["close"] = temp_df["close"].astype(float)
            self.data = pd.concat([self.data, temp_df], ignore_index=True)
            
            # تحديث `start_time` إلى وقت آخر نقطة بيانات تم الحصول عليها
            start_time_str = int(temp_df["timestamp"].iloc[-1]) + 1
            
            print(f"تم جمع {len(temp_df)} نقطة بيانات من {self.symbol} حتى الآن. الاستمرار في الجمع...")

            # التأكد من عدم تجاوز `end_time`
            if datetime.utcfromtimestamp(start_time_str / 1000) >= end_time:
                break

        print(f"تم جمع البيانات التاريخية بنجاح لآخر {self.years} سنوات")

    def prepare_data_for_training(self):
        """إعداد البيانات لاستخدامها في تدريب الاستراتيجيات"""
        return self.data["close"].tolist()


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
