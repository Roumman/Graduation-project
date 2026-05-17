import sqlite3
from datetime import datetime, timedelta
import random
import hashlib

def create_bank_database(db_path="Bank_DB.db"):
    """Создание всей структуры БД банковской системы"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
            transaction_type TEXT NOT NULL, -- 'deposit', 'withdrawal', 'transfer_out', 'transfer_in'
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
            status TEXT DEFAULT 'active', -- 'active', 'paid', 'overdue'
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
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status TEXT DEFAULT 'active', -- 'active', 'closed'
            FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
        )
    ''')

    # НОВЫЕ ТАБЛИЦЫ:

    # Таблица графика платежей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_schedule (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER,
            deposit_id INTEGER,
            payment_date DATE NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending', -- 'pending', 'paid', 'overdue'
            paid_date TIMESTAMP,
            FOREIGN KEY (loan_id) REFERENCES loan(loan_id) ON DELETE CASCADE,
            FOREIGN KEY (deposit_id) REFERENCES deposit(deposit_id) ON DELETE CASCADE
        )
    ''')

    # Таблица выписки по счёту
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_statement (
            statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_id INTEGER,
            operation_type TEXT NOT NULL, -- 'deposit', 'withdrawal', 'interest', 'fee'
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            FOREIGN KEY (account_id) REFERENCES account(account_id) ON DELETE CASCADE,
            FOREIGN KEY (transaction_id) REFERENCES account_transaction(transaction_id) ON DELETE SET NULL
        )
    ''')

    # Таблица расчёта процентов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interest_calculation (
            calculation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deposit_id INTEGER,
            loan_id INTEGER,
            calculation_date DATE NOT NULL,
            interest_amount REAL NOT NULL,
            applied_to_account INTEGER, -- ID счёта, куда зачислены проценты
            FOREIGN KEY (deposit_id) REFERENCES deposit(deposit_id) ON DELETE CASCADE,
            FOREIGN KEY (loan_id) REFERENCES loan(loan_id) ON DELETE CASCADE,
            FOREIGN KEY (applied_to_account) REFERENCES account(account_id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    return conn

def hash_password(password):
    """Хеширование пароля с использованием SHA‑256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def generate_account_number():
    """Генерация уникального номера счёта"""
    return f"ACC-{random.randint(100000, 999999)}"

def populate_database(conn):
    """Заполнение базы данных тестовыми данными"""
    cursor = conn.cursor()

    # Список тестовых данных
    FIRST_NAMES = ['Иван', 'Пётр', 'Сергей', 'Дмитрий', 'Алексей', 'Андрей', 'Михаил', 'Владимир', 'Николай', 'Олег']
    LAST_NAMES = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов', 'Попов', 'Васильев', 'Фёдоров', 'Морозов', 'Волков']
    PATRONYMICS = ['Иванович', 'Петрович', 'Сергеевич', 'Дмитриевич', 'Алексеевич', 'Андреевич', 'Михайлович', 'Владимирович', 'Николаевич', 'Олегович']
    EMAIL_DOMAINS = ['gmail.com', 'yandex.ru', 'mail.ru', 'outlook.com']

    def generate_phone():
        return f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"

    def generate_email(first_name, last_name):
        domain = random.choice(EMAIL_DOMAINS)
        return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{domain}"

    def generate_birth_date():
        years_ago = random.randint(18, 70)
        days_ago = years_ago * 365 + random.randint(-180, 180)
        birth_date = datetime.now() - timedelta(days=days_ago)
        return birth_date.strftime('%Y-%m-%d')

    def generate_address():
        streets = ['Ленина', 'Гагарина', 'Советская', 'Мира', 'Центральная', 'Молодёжная']
        return f"г. Москва, ул. {random.choice(streets)}, д. {random.randint(1, 100)}, кв. {random.randint(1, 200)}"


    # Создаём 10 тестовых клиентов
    client_ids = []
    for i in range(10):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        patronymic = random.choice(PATRONYMICS)

        # Данные клиента
        client_data = {
            'last_name': last_name,
            'first_name': first_name,
            'patronymic': patronymic,
            'phone': generate_phone(),
            'email': generate_email(first_name, last_name),
            'address': generate_address(),
            'date_of_birth': generate_birth_date()
        }

        cursor.execute('''
            INSERT INTO client (last_name, first_name, patronymic, phone, email, address, date_of_birth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_data['last_name'],
            client_data['first_name'],
            client_data['patronymic'],
            client_data['phone'],
            client_data['email'],
            client_data['address'],
            client_data['date_of_birth']
        ))

        client_id = cursor.lastrowid
        client_ids.append(client_id)

        # Создаём логин и пароль
        username = f"user{client_id}"
        password_hash = hash_password("password123")

        cursor.execute('''
            INSERT INTO user_login (client_id, username, password_hash)
            VALUES (?, ?, ?)
        ''', (client_id, username, password_hash))

        # Создаём счёт
        account_number = generate_account_number()
        initial_balance = random.uniform(10000, 100000)

        cursor.execute('''
            INSERT INTO account (client_id, account_number, balance)
            VALUES (?, ?, ?)
        ''', (client_id, account_number, initial_balance))

        account_id = cursor.lastrowid

        # Добавляем транзакции для каждого счёта
        transaction_types = ['deposit', 'withdrawal']
        current_balance = initial_balance

        for _ in range(random.randint(3, 7)):
            t_type = random.choice(transaction_types)
            amount = random.uniform(500, 5000)

            if t_type == 'withdrawal' and amount > current_balance:
                amount = current_balance * 0.5  # Не снимаем больше половины

            # Обновляем баланс
            if t_type == 'deposit':
                current_balance += amount
            else:
                current_balance -= amount

            cursor.execute('''
                INSERT INTO account_transaction (account_id, transaction_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (account_id, t_type, amount, f"Тестовая транзакция {t_type}"))

        # Добавляем кредиты для некоторых клиентов (30 % вероятность)
        if random.random() < 0.3:
            loan_amount = random.uniform(50000, 200000)
            interest_rate = round(random.uniform(8.0, 15.0), 2)

            start_date = (datetime.now() - timedelta(days=random.randint(10, 60))).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d')

            cursor.execute('''
                INSERT INTO loan (client_id, amount, remaining_amount, interest_rate, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_id, loan_amount, loan_amount, interest_rate, start_date, end_date))

            loan_id = cursor.lastrowid

            # Создаём график платежей для кредита
            create_payment_schedule_for_loan(cursor, loan_id, loan_amount, start_date, end_date)

        # Добавляем депозиты для некоторых клиентов (25 % вероятность)
        if random.random() < 0.25:
            deposit_amount = random.uniform(30000, 150000)
            interest_rate = round(random.uniform(4.0, 8.0), 2)

            start_date = (datetime.now() - timedelta(days=random.randint(5, 30))).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

            cursor.execute('''
                INSERT INTO deposit (client_id, amount, interest_rate, start_date, end_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (client_id, deposit_amount, interest_rate, start_date, end_date))
            deposit_id = cursor.lastrowid

            # Создаём график платежей для депозита
            create_payment_schedule_for_deposit(cursor, deposit_id, deposit_amount, start_date, end_date)


    conn.commit()

def create_payment_schedule_for_loan(cursor, loan_id, loan_amount, start_date, end_date):
    """Создаёт график платежей для кредита"""
    # Рассчитываем ежемесячный платёж
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    months_count = (end.year - start.year) * 12 + (end.month - start.month)
    monthly_payment = round(loan_amount / months_count, 2)

    current_date = start
    while current_date < end:
        cursor.execute('''
            INSERT INTO payment_schedule (loan_id, payment_date, amount, status)
            VALUES (?, ?, ?, ?)
        ''', (loan_id, current_date.strftime('%Y-%m-%d'), monthly_payment, 'pending'))
        current_date += timedelta(days=30)

def create_payment_schedule_for_deposit(cursor, deposit_id, deposit_amount, start_date, end_date):
    """Создаёт график начисления процентов для депозита"""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    current_date = start + timedelta(days=30)  # Первый платёж через месяц
    while current_date < end:
        # Рассчитываем проценты за месяц
        monthly_interest = round(deposit_amount * 0.07 / 12, 2)  # 7 % годовых

        cursor.execute('''
            INSERT INTO payment_schedule (deposit_id, payment_date, amount, status)
            VALUES (?, ?, ?, ?)
        ''', (deposit_id, current_date.strftime('%Y-%m-%d'), monthly_interest, 'pending'))
        current_date += timedelta(days=30)

if __name__ == "__main__":
    print("Создание базы данных банковской системы...")
    conn = create_bank_database()
    print("Заполнение базы данных тестовыми данными...")
    populate_database(conn)
    conn.close()
    print("База данных успешно создана и заполнена!")
