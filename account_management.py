import sqlite3

class AccountManagement:
    def __init__(self, db_name='trading_bot.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_account_table()

    def setup_account_table(self):
        """إنشاء جدول الحسابات إذا لم يكن موجودًا"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_type TEXT,
                balance REAL,
                risk_level REAL
            )
        ''')
        self.conn.commit()

    def create_account(self, account_type, balance, risk_level):
        """إنشاء حساب جديد"""
        self.cursor.execute('''
            INSERT INTO Accounts (account_type, balance, risk_level)
            VALUES (?, ?, ?)
        ''', (account_type, balance, risk_level))
        self.conn.commit()
        print(f"تم إنشاء الحساب بنجاح: {account_type} برصيد {balance} ومستوى مخاطرة {risk_level}")

    def update_balance(self, account_id, new_balance):
        """تحديث رصيد الحساب"""
        self.cursor.execute('''
            UPDATE Accounts
            SET balance = ?
            WHERE account_id = ?
        ''', (new_balance, account_id))
        self.conn.commit()
        print(f"تم تحديث الرصيد للحساب {account_id} إلى {new_balance}")

    def get_account_info(self, account_id):
        """استرجاع معلومات الحساب"""
        self.cursor.execute('SELECT * FROM Accounts WHERE account_id = ?', (account_id,))
        return self.cursor.fetchone()

    def __del__(self):
        """إغلاق الاتصال بقاعدة البيانات عند الانتهاء"""
        self.conn.close()
