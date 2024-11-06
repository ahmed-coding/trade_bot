import os
import importlib
from account_management import AccountManagement
from trade_management import TradeManagement
from historical_data_analysis import HistoricalDataAnalyzer
from currency_selection import CurrencySelector
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

class TradingBot:
    def __init__(self, is_virtual=True):
        self.account_manager = AccountManagement()
        self.trade_manager = TradeManagement(is_virtual=is_virtual)
        self.is_virtual = is_virtual
        self.strategies = self.load_strategies()
        self.selected_currencies = []
        self.account_id = self.setup_account(is_virtual)

    def setup_account(self, is_virtual):
        account_type = "virtual" if is_virtual else "real"
        balance = 100000 if is_virtual else 1000  # إعدادات وهمية
        risk_level = 0.01
        self.account_manager.create_account(account_type, balance, risk_level)
        return self.account_manager.get_account_info(1)[0]

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

    def run_strategy(self, strategy_name, data, symbol, quantity=0.001):
        strategy_class = self.strategies.get(strategy_name)
        if strategy_class:
            strategy = strategy_class(data)
            if strategy.should_enter_trade():
                confirmations = self.get_confirmations(strategy.trade_type, data)
                if confirmations >= 2:
                    self.trade_manager.open_trade(symbol, strategy.trade_type, quantity)
                    print(f"تم فتح صفقة على {symbol} بناءً على استراتيجية {strategy_name}")

    def get_confirmations(self, trade_type, data):
        confirmations = 0
        for strategy_name, strategy_class in self.strategies.items():
            strategy = strategy_class(data)
            if strategy.trade_type == trade_type and strategy.should_enter_trade():
                confirmations += 1
        return confirmations

    def execute_trading_cycle(self):
        for currency in self.selected_currencies:
            analyzer = HistoricalDataAnalyzer(symbol=currency, interval="1h", min_history_days=30)
            analyzer.fetch_historical_data()
            data = analyzer.prepare_data_for_training()

            if data is None:
                print(f"البيانات غير كافية للرمز {currency}، تجاوز التحليل.")
                continue

            # اختيار عمود الإغلاق فقط لتغذية الاستراتيجيات
            close_prices = data["close"].tolist()  # تحويل أسعار الإغلاق إلى قائمة

            for strategy_name in self.strategies.keys():
                self.run_strategy(strategy_name, close_prices, currency)
        print("دورة التداول اكتملت.")

if __name__ == "__main__":
    bot = TradingBot(is_virtual=True)
    bot.select_currencies(max_currencies=5)  # اختيار العملات بشكل ديناميكي
    bot.execute_trading_cycle()  # بدء التداول
