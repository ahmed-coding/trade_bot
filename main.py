from account_management import AccountManagement
from trade_management import TradeManagement
from historical_data_analysis import HistoricalDataAnalyzer
from currency_selection import CurrencySelector
from strategies.fibonacci_strategy_ai import FibonacciStrategyAI
# استيراد بقية الاستراتيجيات حسب الحاجة

class TradingBot:
    def __init__(self, is_virtual=True):
        self.account_manager = AccountManagement()
        self.trade_manager = TradeManagement()
        self.is_virtual = is_virtual
        self.strategies = {
            "Fibonacci": FibonacciStrategyAI,
            # أضف بقية الاستراتيجيات هنا
        }
        self.selected_currencies = []
        self.account_id = self.setup_account(is_virtual)

    def setup_account(self, is_virtual):
        account_type = "virtual" if is_virtual else "real"
        balance = 100000 if is_virtual else 1000  # إعدادات وهمية
        risk_level = 0.01
        self.account_manager.create_account(account_type, balance, risk_level)
        return self.account_manager.get_account_info(1)[0]  # ID الحساب

    def select_currencies(self, max_currencies=50):
        selector = CurrencySelector()
        selector.select_currencies(max_currencies)
        self.selected_currencies = selector.get_selected_symbols()

    def run_strategy(self, strategy_name, data, symbol):
        strategy_class = self.strategies.get(strategy_name)
        if strategy_class:
            strategy = strategy_class(data)
            if strategy.should_enter_trade():
                confirmations = self.get_confirmations(strategy.trade_type, data)
                if confirmations >= 2:
                    self.trade_manager.open_trade(symbol, data[-1], strategy_name)
                    print(f"تم فتح صفقة على {symbol} بناءً على استراتيجية {strategy_name}")

    def get_confirmations(self, trade_type, data):
        confirmations = 0
        for name, strategy_class in self.strategies.items():
            strategy = strategy_class(data)
            if strategy.trade_type == trade_type and strategy.should_enter_trade():
                confirmations += 1
        return confirmations

    def execute_trading_cycle(self):
        for currency in self.selected_currencies:
            # جمع البيانات التاريخية للعملة
            analyzer = HistoricalDataAnalyzer(symbol=currency, interval="1d", years=1)
            analyzer.fetch_historical_data()
            data = analyzer.prepare_data_for_training()
            
            for strategy_name in self.strategies.keys():
                self.run_strategy(strategy_name, data, currency)
        print("دورة التداول اكتملت.")

if __name__ == "__main__":
    bot = TradingBot(is_virtual=True)
    bot.select_currencies(max_currencies=50)  # اختيار العملات بشكل ديناميكي
    bot.execute_trading_cycle()  # بدء التداول
