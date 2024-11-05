import os
import sqlite3
from datetime import datetime
from binance.client import Client

class TradeManagement:
    def __init__(self, db_name='trading_bot.db', is_virtual=True):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_trades_table()
        self.is_virtual = is_virtual

        # مفاتيح API الخاصة بالتداول الوهمي
        api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
        
        # تكوين الاتصال بـ Binance Testnet
        if self.is_virtual:
            api_key = os.getenv("BINANCE_TESTNET_API_KEY")
            api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
            self.client = Client(api_key, api_secret, testnet=True)
            self.client.API_URL = 'https://testnet.binance.vision/api'
        else:
            api_key = os.getenv("BINANCE_API_KEY")
            api_secret = os.getenv("BINANCE_API_SECRET")
            self.client = Client(api_key, api_secret)
            

    def setup_trades_table(self):
        """إنشاء جدول الصفقات إذا لم يكن موجودًا"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                entry_price REAL,
                exit_price REAL,
                profit_loss REAL,
                trade_type TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def open_trade(self, symbol, trade_type, quantity):
        """فتح صفقة جديدة على testnet"""
        try:
            order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
            entry_price = float(order['fills'][0]['price'])
            self.cursor.execute('''
                INSERT INTO Trades (symbol, entry_price, trade_type, status)
                VALUES (?, ?, ?, 'open')
            ''', (symbol, entry_price, trade_type))
            self.conn.commit()
            print(f"تم فتح صفقة جديدة على {symbol} بسعر دخول {entry_price}")
        except Exception as e:
            print(f"خطأ أثناء فتح الصفقة: {e}")

    def close_trade(self, trade_id, symbol, quantity):
        """إغلاق صفقة على testnet"""
        try:
            order = self.client.order_market_sell(symbol=symbol, quantity=quantity)
            exit_price = float(order['fills'][0]['price'])
            self.cursor.execute('''
                UPDATE Trades
                SET exit_price = ?, profit_loss = exit_price - entry_price, status = 'closed'
                WHERE trade_id = ? AND status = 'open'
            ''', (exit_price, trade_id))
            self.conn.commit()
            print(f"تم إغلاق الصفقة {trade_id} بسعر خروج {exit_price}")
        except Exception as e:
            print(f"خطأ أثناء إغلاق الصفقة: {e}")

    def get_open_trades(self):
        """استرجاع جميع الصفقات المفتوحة"""
        self.cursor.execute('SELECT * FROM Trades WHERE status = "open"')
        return self.cursor.fetchall()

    def get_trade_history(self):
        """استرجاع جميع الصفقات المغلقة"""
        self.cursor.execute('SELECT * FROM Trades WHERE status = "closed"')
        return self.cursor.fetchall()

    def __del__(self):
        """إغلاق الاتصال بقاعدة البيانات عند الانتهاء"""
        self.conn.close()
