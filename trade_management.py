import sqlite3
from datetime import datetime

class TradeManagement:
    def __init__(self, db_name='trading_bot.db'):
        """تهيئة اتصال قاعدة البيانات"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def open_trade(self, symbol, entry_price, trade_type, trade_duration):
        """فتح صفقة جديدة وتسجيلها في قاعدة البيانات"""
        self.cursor.execute('''
            INSERT INTO Trades (symbol, entry_price, trade_type, trade_duration, status, timestamp)
            VALUES (?, ?, ?, ?, 'open', ?)
        ''', (symbol, entry_price, trade_type, trade_duration, datetime.now()))
        self.conn.commit()
        print(f"تم فتح صفقة جديدة على {symbol} بسعر دخول {entry_price}")

    def close_trade(self, trade_id, exit_price):
        """إغلاق صفقة بناءً على ID الخاص بها"""
        self.cursor.execute('''
            UPDATE Trades
            SET exit_price = ?, profit_loss = exit_price - entry_price, status = 'closed', timestamp = ?
            WHERE id = ? AND status = 'open'
        ''', (exit_price, datetime.now(), trade_id))
        self.conn.commit()
        print(f"تم إغلاق الصفقة برقم {trade_id} بسعر خروج {exit_price}")

    def get_open_trades(self):
        """استرجاع جميع الصفقات المفتوحة"""
        self.cursor.execute('SELECT * FROM Trades WHERE status = "open"')
        trades = self.cursor.fetchall()
        print("الصفقات المفتوحة:")
        for trade in trades:
            print(trade)
        return trades

    def get_closed_trades(self):
        """استرجاع جميع الصفقات المغلقة"""
        self.cursor.execute('SELECT * FROM Trades WHERE status = "closed"')
        trades = self.cursor.fetchall()
        print("الصفقات المغلقة:")
        for trade in trades:
            print(trade)
        return trades

    def __del__(self):
        """إغلاق الاتصال بقاعدة البيانات عند انتهاء الجلسة"""
        self.conn.close()




if __name__ == "__main__":
    trade_manager = TradeManagement()

    # فتح صفقة جديدة
    trade_manager.open_trade("BTCUSDT", 45000, "long", "short_term")

    # استرجاع الصفقات المفتوحة
    trade_manager.get_open_trades()

    # إغلاق الصفقة برقم ID 1 على سبيل المثال
    trade_manager.close_trade(1, 45500)

    # استرجاع الصفقات المغلقة
    trade_manager.get_closed_trades()
