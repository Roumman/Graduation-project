import sqlite3
import hashlib
from datetime import datetime, timedelta

class BankDatabase:
    def __init__(self, db_path="bank.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Создание таблиц базы данных при первом запуске"""
        cursor = self.conn.cursor()

        # Таблица клиентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client (
                client_id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                patronymic TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                date_of_birth DATE NOT NULL
            )
        ''')

        # Таблица логинов пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_login (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                FOREIGN KEY (client_id) REFERENCES client (client_id)
            )
        ''')

        # Таблица счетов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                balance REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'RUB',
                interest_rate REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (client_id) REFERENCES client (client_id)
            )
        ''')

        # Таблица транзакций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_account_id INTEGER,
                to_account_id INTEGER,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_account_id) REFERENCES account (account_id),
                FOREIGN KEY (to_account_id) REFERENCES account (account_id)
            )
        ''')

        # Таблица кредитов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                interest_rate REAL NOT NULL,
                term_months INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                remaining_amount REAL NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (client_id) REFERENCES client (client_id)
            )
        ''')

        # Таблица депозитов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deposits (
                deposit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                interest_rate REAL NOT NULL,
                maturity_date DATE NOT NULL,
                auto_renew BOOLEAN DEFAULT FALSE,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (client_id) REFERENCES client (client_id)
            )
        ''')

        # Таблица карт
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                card_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                card_number TEXT UNIQUE NOT NULL,
                expiry_date DATE NOT NULL,
                cvv TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (account_id) REFERENCES account (account_id)
            )
        ''')

        self.conn.commit()