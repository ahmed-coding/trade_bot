# optimization/trade_performance.py

import sqlite3
import pandas as pd

class TradePerformance:
    def __init__(self, db_path='trading_bot.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def calculate_total_performance(self):
        """حساب إجمالي الأداء لجميع التداولات"""
        df = pd.read_sql_query("SELECT * FROM Trades WHERE status = 'closed'", self.conn)
        if df.empty:
            print("لا توجد بيانات تداول مغلقة لتحليل الأداء.")
            return
        total_profit_loss = df['profit_loss'].sum()
        print(f"إجمالي الربح/الخسارة لجميع التداولات: {total_profit_loss}")
        return total_profit_loss

    def calculate_strategy_performance(self, strategy_name):
        """حساب أداء استراتيجية معينة"""
        df = pd.read_sql_query("SELECT * FROM Trades WHERE status = 'closed' AND trade_type = ?", self.conn, params=(strategy_name,))
        if df.empty:
            print(f"لا توجد بيانات لتداولات استراتيجية {strategy_name} للتحليل.")
            return
        total_profit_loss = df['profit_loss'].sum()
        print(f"إجمالي الربح/الخسارة لاستراتيجية {strategy_name}: {total_profit_loss}")
        return total_profit_loss

    def calculate_average_performance(self):
        """حساب متوسط الربح/الخسارة لكل صفقة مغلقة"""
        df = pd.read_sql_query("SELECT * FROM Trades WHERE status = 'closed'", self.conn)
        if df.empty:
            print("لا توجد بيانات تداول مغلقة لتحليل الأداء.")
            return
        avg_profit_loss = df['profit_loss'].mean()
        print(f"متوسط الربح/الخسارة لكل صفقة: {avg_profit_loss}")
        return avg_profit_loss

    def close(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        self.conn.close()

    def __del__(self):
        """إغلاق الاتصال بقاعدة البيانات عند الانتهاء"""
        self.conn.close()