import sqlite3

class AccountManagement:
    def __init__(self, db_name='trading_bot.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False, timeout=10)  # إضافة timeout لتجنب "database is locked"
        self.cursor = self.conn.cursor()
        self.setup_account_table()

    def setup_account_table(self):
        """إنشاء جدول الحسابات إذا لم يكن موجودًا"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_type TEXT UNIQUE,
                balance REAL,
                risk_level REAL
            )
        ''')
        self.conn.commit()

    def get_or_create_account(self, account_type, balance, risk_level):
        """الحصول على حساب موجود أو إنشاؤه إذا لم يكن موجودًا"""
        # التحقق إذا كان الحساب موجودًا
        self.cursor.execute('SELECT * FROM Accounts WHERE account_type = ?', (account_type,))
        account = self.cursor.fetchone()

        if account:
            print(f"تم العثور على حساب {account_type} موجود.")
            return account  # إعادة معلومات الحساب الموجود

        # إذا لم يكن الحساب موجودًا، يتم إنشاؤه
        self.cursor.execute('''
            INSERT INTO Accounts (account_type, balance, risk_level)
            VALUES (?, ?, ?)
        ''', (account_type, balance, risk_level))
        self.conn.commit()
        print(f"تم إنشاء الحساب بنجاح: {account_type} برصيد {balance} ومستوى مخاطرة {risk_level}")
        return self.cursor.lastrowid, account_type, balance, risk_level

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
