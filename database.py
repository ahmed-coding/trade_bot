import sqlite3

# الاتصال بقاعدة البيانات أو إنشاؤها إذا لم تكن موجودة
conn = sqlite3.connect('trading_bot.db')
cursor = conn.cursor()

# إنشاء جدول الصفقات
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        entry_price REAL,
        exit_price REAL,
        profit_loss REAL,
        trade_type TEXT,
        trade_duration TEXT,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# إنشاء جدول الاستراتيجيات
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Strategies (
        strategy_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        parameters TEXT
    )
''')

# إنشاء جدول الحسابات
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_type TEXT,
        balance REAL,
        risk_level REAL
    )
''')

# إنشاء جدول العملات
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Assets (
        symbol TEXT PRIMARY KEY,
        historical_data TEXT,
        analysis_score REAL
    )
''')

# تأكيد التعديلات وإغلاق الاتصال بقاعدة البيانات
conn.commit()
conn.close()
