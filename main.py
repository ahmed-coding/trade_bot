import os
import importlib
import concurrent.futures
import threading
import time
import math
from account_management import AccountManagement
from trade_management.trade_management import TradeManagement
from historical_data_analysis import HistoricalDataAnalyzer
from currency_selection import CurrencySelector
from dotenv import load_dotenv
from binance.client import Client

# تحميل المتغيرات البيئية
load_dotenv()

class TradingBot:
    def __init__(self, is_virtual=True, enable_short_term=True, enable_long_term=True):
        self.enable_short_term = enable_short_term
        self.enable_long_term = enable_long_term
        self.account_manager = AccountManagement()
        self.trade_manager = TradeManagement(is_virtual=is_virtual)
        self.is_virtual = is_virtual
        self.strategies = self.load_strategies()
        self.selected_currencies = []
        self.account_id, _, _, _ = self.setup_account(is_virtual)
        self.client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))
        self.client.API_URL = 'https://testnet.binance.vision/api' if is_virtual else 'https://api.binance.com'
        self.excluded_symbols = set()
        self.lock = threading.Lock()
        self.current_prices = {} 

    def setup_account(self, is_virtual):
        account_type = "virtual" if is_virtual else "real"
        balance = 10000 if is_virtual else 1000
        risk_level = 0.01
        return self.account_manager.get_or_create_account(account_type, balance, risk_level)
    
    def load_strategies(self):
        strategies = {}
        strategies_path = "./strategies"
        
        def convert_to_camel_case(filename):
            base_name = filename.replace("_ai", "").replace(".py", "")
            return ''.join([part.capitalize() for part in base_name.split('_')]) + "AI"

        for filename in os.listdir(strategies_path):
            if filename.endswith("_strategy_ai.py"):
                module_name = filename[:-3]
                module_path = f"strategies.{module_name}"
                try:
                    strategy_module = importlib.import_module(module_path)
                except ModuleNotFoundError:
                    print(f"تحذير: الملف {module_name} لم يتم تحميله بشكل صحيح.")
                    continue
                class_name = convert_to_camel_case(filename)
                try:
                    strategy_class = getattr(strategy_module, class_name)
                    strategies[class_name] = strategy_class
                except AttributeError:
                    print(f"تحذير: لم يتم العثور على الفئة {class_name} في الملف {filename}.")
        
        print("تم تحميل الاستراتيجيات التالية:", list(strategies.keys()))
        print("تم تحميل إجمالي الاستراتيجيات :", len(list(strategies)))
        
        return strategies

    def select_currencies(self, max_currencies=150):
        selector = CurrencySelector()
        selector.select_currencies(max_currencies)
        self.selected_currencies = selector.get_selected_symbols()

    def adjust_quantity(self, symbol, quantity):
        step_size = self.get_lot_size(symbol)
        if step_size is None:
            return quantity
        precision = int(round(-math.log(step_size, 10), 0))
        return round(quantity, precision)

    def get_lot_size(self, symbol):
        exchange_info = self.client.get_symbol_info(symbol)
        for filter in exchange_info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                step_size = float(filter['stepSize'])
                return step_size
        return None

    def run_strategy(self, strategy_name, data, symbol, volumes=None, moon_phase=None, quantity=0.001):
        strategy_class = self.strategies.get(strategy_name)
        if strategy_class:
            support_level = min(data)
            resistance_level = max(data)

            is_short_term = strategy_class.timeframe == 'short'
            is_long_term = strategy_class.timeframe == 'long'
            
            if (is_short_term and not self.enable_short_term) or (is_long_term and not self.enable_long_term):
                print(f"تجاوز تنفيذ {strategy_name}؛ ليس ضمن الصفقات المحددة.")
                return

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
                confirmations = self.get_confirmations(strategy.timeframe, data, volumes=volumes, moon_phase=moon_phase)
                if confirmations >= 7:
                    stop_loss = support_level * (1 - 0.02)
                    take_profit = resistance_level * (1 + 0.04)
                    quantity = self.adjust_quantity(symbol, quantity)
                    try:
                        with self.lock:
                            self.trade_manager.open_trade(symbol, strategy.trade_type, quantity, strategy_name, stop_loss, take_profit)
                        print(f"تم فتح صفقة على {symbol} بناءً على استراتيجية {strategy_name}")
                    except Exception as e:
                        print(f"خطأ أثناء فتح الصفقة: {e}")
            time.sleep(2)
            
    def get_confirmations(self, trade_type, data, volumes=None, moon_phase=None):
        confirmations = 0
        support_level = min(data)
        resistance_level = max(data)

        for strategy_name, strategy_class in self.strategies.items():
            if strategy_class.__name__ == "DivergenceStrategyAI" and volumes is not None:
                strategy = strategy_class(data, volumes)
            elif strategy_class.__name__ == "MoonPhasesStrategyAI" and moon_phase is not None:
                strategy = strategy_class(data, moon_phase)
            elif strategy_class.__name__ == "SupportResistanceStrategyAI":
                strategy = strategy_class(data, support_level, resistance_level)
            elif strategy_class.__name__ == "VolumeIndicatorsStrategyAI" and volumes is not None:
                strategy = strategy_class(data, volumes)
            else:
                strategy = strategy_class(data)

            if (trade_type == 'short' and not self.enable_short_term) or (trade_type == 'long' and not self.enable_long_term):
                continue
            
            if strategy.timeframe == trade_type and strategy.should_enter_trade():
            # if strategy.should_enter_trade():
                confirmations += 1
        return confirmations

    def execute_trading_cycle(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.analyze_currency, currency) for currency in self.selected_currencies]
            concurrent.futures.wait(futures)
        
        self.improve_strategies()
        self.trade_manager.monitor_trades()
        print("دورة التداول اكتملت.")

    def analyze_currency(self, currency):
        analyzer = HistoricalDataAnalyzer(symbol=currency)
        analyzer.fetch_historical_data()
        data = analyzer.get_data_for_training()

        if data is None:
            print(f"البيانات غير كافية للرمز {currency}، تجاوز التحليل.")
            return

        for interval in analyzer.intervals:
            print(f"تحليل البيانات للرمز {currency}، الإطار الزمني: {interval}")
            close_prices = analyzer.get_close_prices(interval)
            volumes = data[interval]["volume"].tolist() if "volume" in data[interval].columns else None

            for strategy_name in self.strategies.keys():
                self.run_strategy(strategy_name, close_prices, currency, volumes=volumes)



    def update_prices(self):
        """تحديث الأسعار الحالية لجميع العملات المحددة."""
        for symbol in self.selected_currencies:
            try:
                price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
                self.current_prices[symbol] = price
                print(f"تم تحديث السعر لعملة {symbol}: {price}")
            except Exception as e:
                print(f"خطأ في تحديث السعر لـ {symbol}: {e}")
    
    
    def improve_strategies(self):
        for strategy_name in self.strategies.keys():
            self.trade_manager.analyze_performance(strategy_name)
            self.trade_manager.cursor.execute("SELECT average_profit, average_loss, win_rate FROM Performance WHERE strategy_name = ? ORDER BY timestamp DESC LIMIT 1", (strategy_name,))
            performance = self.trade_manager.cursor.fetchone()
            
            if not performance:
                continue

            average_profit, average_loss, win_rate = performance
            strategy = self.strategies[strategy_name]
            
            if win_rate < 0.5:
                strategy.adjust_parameters(risk_level=0.01)
                print(f"تحسين الاستراتيجية {strategy_name} بناءً على نسبة نجاح منخفضة.")
            elif average_profit > abs(average_loss):
                strategy.adjust_parameters(risk_level=0.02)
                print(f"تحسين الاستراتيجية {strategy_name} لتحقيق ربح أكبر.")
            else:
                print(f"لا حاجة لتحسينات إضافية في الاستراتيجية {strategy_name}.")

    def run_continuous_trading(self, interval=60):
        """تشغيل البوت بشكل متواصل"""
        while True:
            try:
                # self.execute_trading_cycle()
                self.update_prices()
                self.monitor_trades()  # مراقبة وإغلاق الصفقات

            except Exception as e:
                print(f"خطأ أثناء دورة التداول: {e}")
            time.sleep(interval)


    def monitor_trades(self):
        """مراقبة وإغلاق الصفقات المفتوحة عند الوصول إلى أهداف الربح أو الخسارة"""
        open_trades = self.trade_manager.get_open_trades()
        for trade_id, symbol, entry_price, stop_loss, take_profit in open_trades:
            current_price = self.current_prices.get(symbol)  # الحصول على السعر الحالي من القاموس
            
            if current_price is None:
                continue  # تخطي إذا لم يتوفر سعر حالي

            # تحقق من الوصول إلى هدف الربح أو وقف الخسارة
            if current_price >= take_profit:
                self.trade_manager.close_trade(trade_id, current_price, "ربح")
            elif current_price <= stop_loss:
                self.trade_manager.close_trade(trade_id, current_price, "خسارة")


if __name__ == "__main__":
    bot = TradingBot(is_virtual=True)
    while True:
        bot.select_currencies(max_currencies=100)
        for currency in bot.selected_currencies:
            
            bot.analyze_currency(currency) # تنفيذ كل دقيقة
        time.sleep(5)