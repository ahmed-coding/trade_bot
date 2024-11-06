cursor.execute('''
    CREATE TABLE IF NOT EXISTS Strategies (
        strategy_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        parameters TEXT
    )
''')
