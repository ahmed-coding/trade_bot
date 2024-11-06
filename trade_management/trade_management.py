import os
import sqlite3
from datetime import datetime
from binance.client import Client

class TradeManagement:
    def __init__(self, db_name='trading_bot.db', is_virtual=True):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()
        self.setup_performance_table()
        self.is_virtual = is_virtual
        self.account_id = self.get_or_create_account(is_virtual)  # الحصول على حساب موجود أو إنشاؤه

        # إعداد مفاتيح API الخاصة بـ Binance بناءً على وضع الحساب (وهمي أو حقيقي)
        api_key = os.getenv("BINANCE_TESTNET_API_KEY" if is_virtual else "BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_TESTNET_API_SECRET" if is_virtual else "BINANCE_API_SECRET")
        self.client = Client(api_key, api_secret, testnet=is_virtual)
        if is_virtual:
            self.client.API_URL = 'https://testnet.binance.vision/api'

    def setup_tables(self):
        """إنشاء الجداول اللازمة إذا لم تكن موجودة"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_type TEXT UNIQUE,
                balance REAL,
                risk_level REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                entry_price REAL,
                exit_price REAL,
                profit_loss REAL,
                trade_type TEXT,
                trade_duration TEXT,
                strategy_name TEXT,  -- إضافة العمود لتسجيل اسم الاستراتيجية
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def get_or_create_account(self, is_virtual):
        """الحصول على حساب موجود أو إنشاء حساب جديد إذا لم يكن موجودًا"""
        account_type = "virtual" if is_virtual else "real"
        self.cursor.execute("SELECT account_id FROM Accounts WHERE account_type = ?", (account_type,))
        account = self.cursor.fetchone()

        if account:
            print(f"تم العثور على حساب {account_type} موجود.")
            return account[0]  # إرجاع account_id للحساب الموجود

        # إذا لم يكن الحساب موجودًا، يتم إنشاؤه
        balance = 100000 if is_virtual else 1000  # رصيد افتراضي للحساب
        risk_level = 0.01  # مستوى المخاطرة الافتراضي
        self.cursor.execute('''
            INSERT INTO Accounts (account_type, balance, risk_level)
            VALUES (?, ?, ?)
        ''', (account_type, balance, risk_level))
        self.conn.commit()
        print(f"تم إنشاء حساب {account_type} جديد.")
        return self.cursor.lastrowid  # إرجاع account_id للحساب الجديد



    def open_trade(self, symbol, trade_type, quantity, strategy_name):
        """فتح صفقة جديدة على testnet مع تسجيل اسم الاستراتيجية"""
        try:
            order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
            entry_price = float(order['fills'][0]['price'])
            self.cursor.execute('''
                INSERT INTO Trades (symbol, entry_price, trade_type, strategy_name, status)
                VALUES (?, ?, ?, ?, 'open')
            ''', (symbol, entry_price, trade_type, strategy_name))
            self.conn.commit()
            print(f"تم فتح صفقة جديدة على {symbol} بسعر دخول {entry_price} باستخدام الاستراتيجية {strategy_name}")
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
                WHERE trade_id = ? AND status = 'open' AND account_id = ?
            ''', (exit_price, trade_id, self.account_id))
            self.conn.commit()
            print(f"تم إغلاق الصفقة {trade_id} بسعر خروج {exit_price}")
        except Exception as e:
            print(f"خطأ أثناء إغلاق الصفقة: {e}")

    def get_open_trades(self):
        """استرجاع جميع الصفقات المفتوحة للحساب"""
        self.cursor.execute('SELECT * FROM Trades WHERE status = "open" AND account_id = ?', (self.account_id,))
        return self.cursor.fetchall()

    def get_trade_history(self):
        """استرجاع جميع الصفقات المغلقة للحساب"""
        self.cursor.execute('SELECT * FROM Trades WHERE status = "closed" AND account_id = ?', (self.account_id,))
        return self.cursor.fetchall()

    def setup_performance_table(self):
        """إعداد جدول الأداء"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Performance (
                performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT,
                total_profit_loss REAL,
                average_profit REAL,
                average_loss REAL,
                win_rate REAL,
                total_trades INTEGER,
                profitable_trades INTEGER,
                unprofitable_trades INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def analyze_performance(self, strategy_name):
        """تحليل الصفقات المغلقة لتحديث أداء الاستراتيجيات"""
        self.cursor.execute("SELECT profit_loss FROM Trades WHERE status = 'closed' AND strategy_name = ?", (strategy_name,))
        closed_trades = self.cursor.fetchall()
        
        if not closed_trades:
            print("لا توجد صفقات مغلقة لتحليل الأداء.")
            return

        profits = [trade[0] for trade in closed_trades if trade[0] > 0]
        losses = [trade[0] for trade in closed_trades if trade[0] <= 0]
        total_trades = len(closed_trades)
        total_profit_loss = sum(profits) + sum(losses)
        average_profit = sum(profits) / len(profits) if profits else 0
        average_loss = sum(losses) / len(losses) if losses else 0
        win_rate = len(profits) / total_trades if total_trades > 0 else 0
        profitable_trades = len(profits)
        unprofitable_trades = len(losses)

        # تسجيل الأداء في جدول Performance
        self.cursor.execute('''
            INSERT INTO Performance (strategy_name, total_profit_loss, average_profit, average_loss, win_rate, 
                                     total_trades, profitable_trades, unprofitable_trades)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (strategy_name, total_profit_loss, average_profit, average_loss, win_rate, total_trades, profitable_trades, unprofitable_trades))
        self.conn.commit()

        print(f"تم تحليل الأداء للاستراتيجية {strategy_name} وتخزين النتائج.")
    def __del__(self):
        """إغلاق الاتصال بقاعدة البيانات عند الانتهاء"""
        self.conn.close()