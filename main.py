import os
import importlib
from account_management import AccountManagement
from trade_management.trade_management import TradeManagement
from historical_data_analysis import HistoricalDataAnalyzer
from currency_selection import CurrencySelector
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

class TradingBot:
    def __init__(self, is_virtual=True, enable_short_term=True, enable_long_term=True):
        # إضافة إعدادات الصفقات قصيرة وطويلة المدى
        self.enable_short_term = enable_short_term
        self.enable_long_term = enable_long_term
        self.account_manager = AccountManagement()
        self.trade_manager = TradeManagement(is_virtual=is_virtual)
        self.is_virtual = is_virtual
        self.strategies = self.load_strategies()
        self.selected_currencies = []
        self.account_id, _, _, _ = self.setup_account(is_virtual)


    def setup_account(self, is_virtual):
        account_type = "virtual" if is_virtual else "real"
        balance = 10000 if is_virtual else 1000  # إعدادات وهمية
        risk_level = 0.01
        return self.account_manager.get_or_create_account(account_type, balance, risk_level)

    def load_strategies(self):
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

    def select_currencies(self, max_currencies=50):
        selector = CurrencySelector()
        selector.select_currencies(max_currencies)
        self.selected_currencies = selector.get_selected_symbols()

    def run_strategy(self, strategy_name, data, symbol, volumes=None, moon_phase=None, quantity=0.001):
        strategy_class = self.strategies.get(strategy_name)
        if strategy_class:
            support_level = min(data)  # مثال على تعيين مستوى دعم افتراضي
            resistance_level = max(data)  # مثال على تعيين مستوى مقاومة افتراضي

    
    # تحقق من نوع الاستراتيجية وطابقها مع الإعدادات
            is_short_term = strategy_class.timeframe == 'short'
            is_long_term = strategy_class.timeframe == 'long'
            
            if (is_short_term and not self.enable_short_term) or (is_long_term and not self.enable_long_term):
                print(f"تجاوز تنفيذ {strategy_name}؛ ليس ضمن الصفقات المحددة.")
                return

            # تنفيذ باقي عملية تشغيل الاستراتيجية بناءً على الإعدادات المتوفرة
            support_level = min(data)
            resistance_level = max(data)

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
                if confirmations >= 2:
                    self.trade_manager.open_trade(symbol, strategy.timeframe, quantity)
                    print(f"تم فتح صفقة على {symbol} بناءً على استراتيجية {strategy_name}")

                    

    def get_confirmations(self, trade_type, data, volumes=None, moon_phase=None):
        confirmations = 0

        support_level = min(data)  # مثال على تعيين مستوى دعم افتراضي
        resistance_level = max(data)  # مثال على تعيين مستوى مقاومة افتراضي

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
                confirmations += 1
                

        return confirmations


    def execute_trading_cycle(self):
        for currency in self.selected_currencies:
            analyzer = HistoricalDataAnalyzer(symbol=currency)
            analyzer.fetch_historical_data()
            data = analyzer.get_data_for_training()

            if data is None:
                print(f"البيانات غير كافية للرمز {currency}، تجاوز التحليل.")
                continue

            for interval in analyzer.intervals:
                print(f"تحليل البيانات للرمز {currency}، الإطار الزمني: {interval}")
                close_prices = analyzer.get_close_prices(interval)
                volumes = data[interval]["volume"].tolist() if "volume" in data[interval].columns else None

                for strategy_name in self.strategies.keys():
                    self.run_strategy(strategy_name, close_prices, currency, volumes=volumes)
            
        # تحليل الأداء بعد كل دورة
        self.trade_manager.analyze_performance()
        print("دورة التداول اكتملت.")


    def improve_all_strategies(self):
        for strategy in self.strategies.values():
            self.trade_manager.improve_strategies(strategy)


if __name__ == "__main__":
    bot = TradingBot(is_virtual=True)
    bot.select_currencies(max_currencies=1)  # اختيار العملات بشكل ديناميكي
    bot.execute_trading_cycle()  # بدء التداول
