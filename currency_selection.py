import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import importlib
class CurrencySelector:
    def __init__(self, intervals=["1h", "4h", "1d"], min_history_days=30):
        """
        :param intervals: قائمة الأطر الزمنية المطلوبة. على سبيل المثال ["1h", "4h", "1d"]
        :param min_history_days: الحد الأدنى من الأيام للبيانات المطلوبة. يمكن تعديله لزيادة المرونة
        """
        self.intervals = intervals
        self.min_history_days = min_history_days
        self.available_symbols = self.fetch_available_symbols()
        self.selected_symbols = []

    def fetch_available_symbols(self):
        """جمع قائمة العملات المتاحة للتداول على Binance"""
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url)
        data = response.json()
        symbols = [item["symbol"] for item in data["symbols"] if item["quoteAsset"] == "USDC"]
        print(f"تم جمع {len(symbols)} عملة من Binance")
        return symbols

    def fetch_currency_data(self, symbol, interval):
        """جمع البيانات التاريخية للإطار الزمني المحدد لكل رمز بشكل متتابع"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.min_history_days)
        start_time_str = int(start_time.timestamp() * 1000)

        url = "https://api.binance.com/api/v3/klines"
        all_data = []
        while True:
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_time_str,
                "limit": 1000
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if not data or len(data) == 0:
                break
            
            all_data.extend(data)
            start_time_str = data[-1][0] + 1  # ضبط الوقت للطلب التالي

            if len(all_data) >= self.min_history_days * 24:
                break

        # حساب العدد الأدنى للبيانات المطلوبة ومرونة 80%
        minimum_required_points = self.min_history_days * (24 if interval == "1h" else (6 if interval == "4h" else 1)) * 0.8
        if len(all_data) < minimum_required_points:
            print(f"البيانات غير كافية للعملة {symbol} للإطار {interval}، تحتوي على {len(all_data)} نقطة بيانات فقط.")
            return None

        df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
        df["close"] = df["close"].astype(float)
        return df

    def is_currency_suitable(self, dfs):
        """تحديد ما إذا كانت العملة مناسبة للتداول عبر تحليل الأطر الزمنية المختلفة"""
        for interval, df in dfs.items():
            trend = df["close"].pct_change().mean()
            volatility = df["close"].pct_change().std()
            if trend <= 0 or volatility >= 0.05:
                return False
        return True

    def select_currencies(self, max_currencies=50):
        """اختيار عدد محدد من العملات للتداول عبر الأطر الزمنية المختلفة"""
        for symbol in self.available_symbols:
            if len(self.selected_symbols) >= max_currencies:
                break
            dfs = {}
            for interval in self.intervals:
                df = self.fetch_currency_data(symbol, interval)
                if df is not None:
                    dfs[interval] = df
                else:
                    break
            if len(dfs) == len(self.intervals) and self.is_currency_suitable(dfs):
                self.selected_symbols.append(symbol)
                print(f"تم اختيار العملة {symbol} للتداول")
        print(f"تم اختيار {len(self.selected_symbols)} عملة للتداول.")

    def get_selected_symbols(self):
        """إرجاع قائمة العملات المختارة"""
        return self.selected_symbols
    
    def train_models(self):
        strategies = load_strategies()
        max_currencies=1
        for symbol in self.available_symbols:
            if len(self.selected_symbols) >=max_currencies:
                break
            dfs = {}
            for interval in self.intervals:
                df = self.fetch_currency_data(symbol, interval)
                if df is not None:
                    dfs[interval] = df
                else:
                    break
            if len(dfs) == len(self.intervals) and self.is_currency_suitable(dfs):
                self.selected_symbols.append(symbol)
                print(f"تم اختيار العملة {symbol} للتداول")
            print(f"تم اختيار {len(self.selected_symbols)} عملة")
            
        
        def load_strategies():
            """تحميل الاستراتيجيات ديناميكيًا من مجلد الاستراتيجيات"""
            strategies = {}
            strategies_path = "./strategies"
            
            def convert_to_camel_case(filename):
                # إزالة لاحقة _ai واللاحقة .py ثم تحويل إلى CamelCase وإضافة "AI" في النهاية
                base_name = filename.replace("_ai", "").replace(".py", "")
                return ''.join([part.capitalize() for part in base_name.split('_')]) + "AI"

            for filename in os.listdir(strategies_path):
                if filename.endswith("_strategy_ai.py"):
                    module_name = filename[:-3]  # إزالة ".py"
                    module_path = f"strategies.{module_name}"
                    
                    # تحميل الملف كـ module
                    try:
                        strategy_module = importlib.import_module(module_path)
                    except ModuleNotFoundError:
                        print(f"تحذير: الملف {module_name} لم يتم تحميله بشكل صحيح.")
                        continue
                    
                    # تحويل الاسم إلى CamelCase وإضافة AI
                    class_name = convert_to_camel_case(filename)
                    # print(f"الملف: {filename}, الفئة المتوقعة: {class_name}")
                    
                    # عرض جميع الكائنات المتاحة في الملف
                    available_classes = [attr for attr in dir(strategy_module) if not attr.startswith("_")]
                    # print(f"الكائنات المتاحة في {filename}: {available_classes}")
                    
                    try:
                        # تحميل الفئة الرئيسية من الملف وإضافتها إلى قاموس الاستراتيجيات
                        strategy_class = getattr(strategy_module, class_name)
                        strategies[class_name] = strategy_class
                        # print(f"تم تحميل الاستراتيجية: {class_name}")
                    except AttributeError:
                        print(f"تحذير: لم يتم العثور على الفئة {class_name} في الملف {filename}. تحقق من تطابق الاسم في الملف.")
            
            print("تم تحميل الاستراتيجيات التالية:", list(strategies.keys()))
            print("تم تحميل إجمالي الاستراتيجيات :", len(list(strategies)))
            
            return strategies
        

        def run_strategy(self, strategy_name, data, symbol, volumes=None, moon_phase=None, quantity=0.001):
                strategy_class = self.strategies.get(strategy_name)
                if strategy_class:
                    support_level = min(data)  # مثال على تعيين مستوى دعم افتراضي
                    resistance_level = max(data)  # مثال على تعيين مستوى مقاومة افتراضي

                    if volumes is not None and 'volumes' in strategy_class.__init__.__code__.co_varnames:
                        strategy = strategy_class(data, volumes)
                    elif moon_phase is not None and 'moon_phase' in strategy_class.__init__.__code__.co_varnames:
                        strategy = strategy_class(data, moon_phase)
                    elif 'support_level' in strategy_class.__init__.__code__.co_varnames and 'resistance_level' in strategy_class.__init__.__code__.co_varnames:
                        strategy = strategy_class(data, support_level, resistance_level)
                    elif strategy_class.__name__ == "VolumeIndicatorsStrategyAI" and volumes is not None:
                        strategy = strategy_class(data, volumes)
                    else:
                        strategy = strategy_class(data)

                    strategy.train_model()
                    if strategy.should_enter_trade():
                        confirmations = self.get_confirmations(strategy.trade_type, data, volumes=volumes, moon_phase=moon_phase)
                        # if confirmations >= 2:
                        #     self.trade_manager.open_trade(symbol, strategy.trade_type, quantity)
                        #     print(f"تم فتح صفقة على {symbol} بناءً على استراتيجية {strategy_name}")
