import os
import sqlite3
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
import math

class TradeManagement:
    def __init__(self, db_name='trading_bot.db', is_virtual=True, max_risk=0.01):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()
        self.setup_performance_table()
        self.is_virtual = is_virtual
        self.account_id = self.get_or_create_account(is_virtual)  # الحصول على حساب موجود أو إنشاؤه
        self.max_risk = max_risk
        self.active_trades = {}


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
                risk REAL,
                trade_duration TEXT,
                strategy_name TEXT, 
                stop_loss REAL,
                take_profit REAL,
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
        balance = 10000 if is_virtual else 1000  # رصيد افتراضي للحساب
        risk_level = 0.01  # مستوى المخاطرة الافتراضي
        self.cursor.execute('''
            INSERT INTO Accounts (account_type, balance, risk_level)
            VALUES (?, ?, ?)
        ''', (account_type, balance, risk_level))
        self.conn.commit()
        print(f"تم إنشاء حساب {account_type} جديد.")
        return self.cursor.lastrowid  # إرجاع account_id للحساب الجديد
    
    def get_account_balance(self):
        """الحصول على رصيد الحساب"""
        balance = self.client.get_asset_balance(asset='USDT')
        return float(balance['free']) if balance else 0.0
    

    def calculate_position_size(self, account_balance, risk):
        """حساب حجم الصفقة بناءً على مستوى المخاطرة"""
        return account_balance * risk
    
    
    # دالة لضبط الكمية بناءً على دقة السوق
    def adjust_quantity(self, symbol, quantity):
        step_size = self.get_lot_size(symbol)
        if step_size is None:
            return quantity
        precision = int(round(-math.log(step_size, 10), 0))
        return round(quantity, precision)

    # دالة للحصول على حجم اللوت للرمز المحدد
    def get_lot_size(self, symbol):
        exchange_info = self.client.get_symbol_info(symbol)
        for filter in exchange_info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                step_size = float(filter['stepSize'])
                return step_size
        return None


    def load_open_trades(self):
        """تحميل الصفقات المفتوحة من قاعدة البيانات إلى active_trades"""
        self.cursor.execute("SELECT id, symbol, entry_price, quantity, stop_loss, take_profit FROM Trades WHERE status = 'open'")
        open_trades = self.cursor.fetchall()
        
        for trade in open_trades:
            trade_id, symbol, entry_price, quantity, stop_loss, take_profit = trade
            self.active_trades[symbol] = {
                'trade_id': trade_id,
                'entry_price': entry_price,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
        print(f"تم تحميل {len(self.active_trades)} صفقة مفتوحة من قاعدة البيانات.")


    def open_trade(self, symbol, trade_type, quantity,strategy_name, stop_loss, take_profit):
        """فتح صفقة جديدة بحساب ديناميكي للكمية بناءً على الرصيد"""
        try:
            # الحصول على الرصيد المتاح
            usdt_balance = float(self.client.get_asset_balance(asset="USDT")["free"])
            entry_price = 0
            # تحديد نسبة المخاطرة من الرصيد
            risk_percentage = 0.01  # على سبيل المثال: 1% من الرصيد
            order_value = usdt_balance * risk_percentage

            # حساب الكمية بناءً على السعر الحالي للرمز
            current_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            quantity = order_value / current_price

            # ضبط الكمية بناءً على دقة السوق
            quantity = self.adjust_quantity(symbol, quantity)

            # تحقق من أن الكمية أكبر من الحد الأدنى المسموح به للشراء
            min_quantity = self.get_lot_size(symbol)
            if quantity < min_quantity:
                print(f"الكمية المحسوبة ({quantity}) أقل من الحد الأدنى المسموح به ({min_quantity}). تجاوز الصفقة.")
                return

            # محاولة فتح الصفقة
            order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
            entry_price = float(order['fills'][0]['price']) 

            """فتح صفقة جديدة"""
            # INSERT INTO Trades (symbol, entry_price, trade_type, strategy_name, stop_loss, take_profit, quantity, status)

            self.cursor.execute('''
                INSERT INTO Trades (symbol, entry_price, trade_type, strategy_name, stop_loss, take_profit, status)
                VALUES (?, ?, ?, ?, ?, ?,  'open')
            ''', (symbol, entry_price, trade_type, strategy_name, stop_loss, take_profit))
            self.conn.commit()
            
            trade_id = self.cursor.lastrowid
            self.active_trades[symbol] = {
                'trade_id': trade_id,
                'entry_price': entry_price,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
            }
            print(f"تم فتح صفقة جديدة على {symbol} بسعر دخول {entry_price} وكمية {quantity}")
            
        except Exception as e:
            print(f"خطأ أثناء فتح الصفقة: {e} في عملة {symbol}")

            # trade_id = self.cursor.lastrowid
            # self.active_trades[symbol] = {
            #     'trade_id': trade_id,
            #     'entry_price': entry_price,
            #     'quantity': quantity,
            #     'stop_loss': stop_loss,
            #     'take_profit': take_profit,
            # }

            # print(f"تم فتح صفقة جديدة على {symbol} بسعر دخول {entry_price} وكمية {quantity}")
        


            
    def close_trade(self, trade_id, exit_price, result):
        """إغلاق صفقة بتحديث السعر النهائي وحالة الربح أو الخسارة"""
        profit_loss = (exit_price - self.entry_price) * self.quantity if result == "ربح" else (self.entry_price - exit_price) * self.quantity
        self.cursor.execute('''
            UPDATE Trades
            SET exit_price = ?, profit_loss = ?, status = "closed"
            WHERE trade_id = ?
        ''', (exit_price, profit_loss, trade_id))
        self.conn.commit()
        print(f"تم إغلاق الصفقة {trade_id} بسعر {exit_price} مع نتيجة {result}")
            

    def get_open_trades(self):
        """استرجاع جميع الصفقات المفتوحة"""
        self.cursor.execute('SELECT id, symbol, entry_price, stop_loss, take_profit FROM Trades WHERE status = "open"')
        return self.cursor.fetchall()

    # باقي الكود...

    def monitor_trades(self):
        """مراقبة الصفقات المفتوحة وتحديث حالتها إذا تحقق الوقف أو جني الأرباح"""
        self.cursor.execute("SELECT id, symbol, entry_price, stop_loss, take_profit FROM Trades WHERE status = 'open'")
        open_trades = self.cursor.fetchall()

        for trade_id, symbol, entry_price, stop_loss, take_profit in open_trades:
            current_price = float(self.client.get_symbol_ticker(symbol=symbol)["price"])

            # تأكد من تحويل stop_loss و take_profit إلى float
            stop_loss = float(stop_loss) if stop_loss is not None else None
            take_profit = float(take_profit) if take_profit is not None else None

            if stop_loss is not None and current_price <= stop_loss:
                print(f"السعر الحالي {current_price} وصل إلى مستوى وقف الخسارة {stop_loss} للصفقة {trade_id}")
                self.close_trade(trade_id, symbol, quantity=0.001)  # تعديل الكمية حسب الحاجة
            elif take_profit is not None and current_price >= take_profit:
                print(f"السعر الحالي {current_price} وصل إلى مستوى جني الأرباح {take_profit} للصفقة {trade_id}")
                self.close_trade(trade_id, symbol, quantity=0.001)  # تعديل الكمية حسب الحاجة

    # def get_open_trades(self):
    #     """استرجاع جميع الصفقات المفتوحة"""
    #     self.cursor.execute('SELECT * FROM Trades WHERE status = "open"')
    #     return self.cursor.fetchall()

    def get_current_price(self, symbol):
        """جلب السعر الحالي من واجهة Binance API"""
        return float(self.client.get_symbol_ticker(symbol=symbol)['price'])

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