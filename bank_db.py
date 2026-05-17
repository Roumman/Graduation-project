import sqlite3
from datetime import datetime, timedelta
import random  # Добавлен импорт random

class BankDatabase:
    def __init__(self, db_path="Bank_DB.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """Создание необходимых таблиц в БД"""
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
                date_of_birth DATE NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица логинов и паролей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_login (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL UNIQUE,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
            )
        ''')

        # Таблица счетов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                type_id INTEGER DEFAULT 1,
                balance REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'RUB',
                status TEXT DEFAULT 'active',
                opened_by TEXT DEFAULT 'system',
                opened_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_date TIMESTAMP,
                interest_rate REAL DEFAULT 0.0,
                FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
            )
        ''')

        # Таблица транзакций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_transaction (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES account(account_id) ON DELETE CASCADE
            )
        ''')

        # Таблица кредитов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loan (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                remaining_amount REAL NOT NULL,
                interest_rate REAL NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
            )
        ''')

        # Таблица депозитов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deposit (
                deposit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                interest_rate REAL NOT NULL,
                startdate DATE NOT NULL,
                enddate DATE NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def create_client(self, last_name, first_name, patronymic, phone, email, address, date_of_birth):
        """Создание записи о клиенте в таблице client"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO client (last_name, first_name, patronymic, phone, email, address, date_of_birth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (last_name, first_name, patronymic, phone, email, address, date_of_birth))
        self.conn.commit()
        return cursor.lastrowid

    def create_user_login(self, client_id, username, password_hash):
        """Создание записи в таблице user_login"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO user_login (client_id, username, password_hash, created_date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (client_id, username, password_hash))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Логин '{username}' уже существует") from e

    def create_account(self, client_id):
        """Создание счёта для клиента с генерацией account_number"""
        cursor = self.conn.cursor()

        # Генерация уникального номера счёта
        account_number = f"ACC-{random.randint(100000, 999999)}"

        cursor.execute('''
            INSERT INTO account (
                client_id, account_number, type_id, balance, currency,
                status, opened_by, interest_rate, opened_date
            ) VALUES (?, ?, 1, 0.0, 'RUB', 'active', 'system', 0.0, CURRENT_TIMESTAMP)
        ''', (client_id, account_number))
        self.conn.commit()
        return cursor.lastrowid  # Возвращаем account_id

    def authenticate_with_password(self, username, password_hash):
        """Аутентификация по логину и хешированному паролю"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.user_id, u.client_id
            FROM user_login u
            JOIN client c ON u.client_id = c.client_id
            WHERE u.username = ? AND u.password_hash = ?
        ''', (username, password_hash))
        result = cursor.fetchone()
        if result:
            return {'user_id': result[0], 'client_id': result[1]}
        return None

    def check_username_exists(self, username):
        """Проверка существования логина"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM user_login WHERE username = ?', (username,))
        return cursor.fetchone() is not None

    def get_client_info(self, client_id):
        """Получение информации о клиенте"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT last_name, first_name, patronymic, phone, email, address
            FROM client
            WHERE client_id = ?
        ''', (client_id,))
        row = cursor.fetchone()
        if row:
            return {
                'last_name': row[0],
                'first_name': row[1],
                'patronymic': row[2],
                'phone': row[3],
                'email': row[4],
                'address': row[5]
            }
        return None

    def get_balance(self, client_id):
        """Получение баланса клиента"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT balance
            FROM account
            WHERE client_id = ?
        ''', (client_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return 0.0

    def withdraw(self, client_id, amount):
        """Снятие наличных с записью в транзакции"""
        current_balance = self.get_balance(client_id)
        if current_balance >= amount:
            cursor = self.conn.cursor()
            # Обновляем баланс
            cursor.execute('''
                UPDATE account
                SET balance = balance - ?
                WHERE client_id = ?
            ''', (amount, client_id))
            # Записываем транзакцию
            account_id = self.get_account_id(client_id)
            cursor.execute('''
                INSERT INTO account_transaction (account_id, transaction_type, amount, description)
                VALUES (?, 'withdrawal', ?, 'Снятие наличных')
            ''', (account_id, amount))
            self.conn.commit()
            return True
        return False

    def deposit(self, client_id, amount):
        """Пополнение счёта с записью в транзакции"""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной!")

        cursor = self.conn.cursor()

        # Обновляем баланс счёта клиента
        cursor.execute('''
            UPDATE account
            SET balance = balance + ?
            WHERE client_id = ?
        ''', (amount, client_id))

        # Проверяем, что обновление прошло успешно (счёт существует)
        if cursor.rowcount == 0:
            raise ValueError("Счёт клиента не найден!")

        # Получаем account_id для записи транзакции
        account_id = self.get_account_id(client_id)
        if not account_id:
            raise ValueError("Не удалось найти счёт клиента для записи транзакции!")

        # Записываем транзакцию в историю
        cursor.execute('''
            INSERT INTO account_transaction (account_id, transaction_type, amount, description)
            VALUES (?, 'deposit', ?, 'Пополнение счёта')
        ''', (account_id, amount))

        self.conn.commit()

    def withdraw(self, client_id, amount):
        """Снятие наличных с проверкой баланса и записью в транзакции"""
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной!")

        current_balance = self.get_balance(client_id)
        if current_balance < amount:
            return False  # Недостаточно средств

        cursor = self.conn.cursor()
        # Обновляем баланс
        cursor.execute('''
            UPDATE account
            SET balance = balance - ?
            WHERE client_id = ?
        ''', (amount, client_id))

        # Записываем транзакцию
        account_id = self.get_account_id(client_id)
        cursor.execute('''
            INSERT INTO account_transaction (account_id, transaction_type, amount, description)
            VALUES (?, 'withdrawal', ?, 'Снятие наличных')
        ''', (account_id, amount))

        self.conn.commit()
        return True

    def transfer(self, from_client_id, to_client_id, amount):
        """Перевод между счетами с проверкой существования получателя и баланса"""
        if amount <= 0:
            raise ValueError("Сумма перевода должна быть положительной!")

        # Проверяем существование получателя
        if not self.client_exists(to_client_id):
            return False

        # Проверяем достаточность средств
        current_balance = self.get_balance(from_client_id)
        if current_balance < amount:
            return False

        cursor = self.conn.cursor()
        try:
            # Снимаем с отправителя
            cursor.execute('''
                UPDATE account
                SET balance = balance - ?
                WHERE client_id = ?
            ''', (amount, from_client_id))

            # Пополняем получателю
            cursor.execute('''
                UPDATE account
                SET balance = balance + ?
                WHERE client_id = ?
            ''', (amount, to_client_id))

            # Записываем транзакции
            from_account = self.get_account_id(from_client_id)
            to_account = self.get_account_id(to_client_id)

            cursor.execute('''
                INSERT INTO account_transaction
                (account_id, transaction_type, amount, description)
                VALUES (?, 'transfer_out', ?, 'Перевод клиенту ' || ?)
            ''', (from_account, amount, to_client_id))

            cursor.execute('''
                INSERT INTO account_transaction
                (account_id, transaction_type, amount, description)
                VALUES (?, 'transfer_in', ?, 'Перевод от клиента ' || ?)
            ''', (to_account, amount, from_client_id))

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_balance(self, client_id):
        """Получение баланса клиента"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT balance
            FROM account
            WHERE client_id = ? AND status = 'active'
        ''', (client_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return 0.0

    def get_account_id(self, client_id):
        """Получение account_id по client_id"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT account_id FROM account WHERE client_id = ?', (client_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

    def client_exists(self, client_id):
        """Проверка существования клиента"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM client WHERE client_id = ?', (client_id,))
        return cursor.fetchone() is not None

    def get_transaction_history(self, client_id, limit=20):
        """Получение истории транзакций клиента"""
        cursor = self.conn.cursor()
        account_id = self.get_account_id(client_id)
        if not account_id:
            return []

        cursor.execute('''
            SELECT transaction_type, amount, description, timestamp
            FROM account_transaction
            WHERE account_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (account_id, limit))

        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'type': row[0],
                'amount': row[1],
                'description': row[2],
                'timestamp': row[3]
            })
        return transactions

    def close(self):
        """Закрытие соединения с БД"""
        if self.conn:
            self.conn.close()
