import sqlite3
import random
from datetime import datetime, timedelta

# Список тестовых данных
FIRST_NAMES = ['Иван', 'Пётр', 'Сергей', 'Дмитрий', 'Алексей', 'Андрей', 'Михаил', 'Владимир', 'Николай', 'Олег']
LAST_NAMES = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов', 'Попов', 'Васильев', 'Фёдоров', 'Морозов', 'Волков']
PATRONYMICS = ['Иванович', 'Петрович', 'Сергеевич', 'Дмитриевич', 'Алексеевич', 'Андреевич', 'Михайлович', 'Владимирович', 'Николаевич', 'Олегович']
EMAIL_DOMAINS = ['gmail.com', 'yandex.ru', 'mail.ru', 'outlook.com']

def generate_phone():
    """Генерация российского номера телефона"""
    return f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"

def generate_email(first_name, last_name):
    """Генерация email на основе имени и фамилии"""
    domain = random.choice(EMAIL_DOMAINS)
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{domain}"


def generate_birth_date():
    """Генерация даты рождения (18–70 лет)"""
    years_ago = random.randint(18, 70)
    days_ago = years_ago * 365 + random.randint(-180, 180)
    birth_date = datetime.now() - timedelta(days=days_ago)
    return birth_date.strftime('%Y-%m-%d')

def generate_address():
    """Генерация адреса"""
    streets = ['Ленина', 'Гагарина', 'Советская', 'Мира', 'Центральная', 'Молодёжная']
    return f"г. Москва, ул. {random.choice(streets)}, д. {random.randint(1, 100)}, кв. {random.randint(1, 200)}"

def generate_unique_username(last_name, first_name, used_usernames):
    """Генерация уникального username"""
    base_username = f"{last_name.lower()}_{first_name.lower()[0]}"
    username = base_username

    # Если такой логин уже есть, добавляем цифру
    counter = 1
    while username in used_usernames:
        username = f"{base_username}{counter}"
        counter += 1

    used_usernames.add(username)
    return username

def main():
    # Подключение к БД
    conn = sqlite3.connect('Bank_DB.db')
    cursor = conn.cursor()

    print("Начинаем заполнение базы данных...")

    # Множество для отслеживания уже использованных логинов
    used_usernames = set()

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

        # Создаём запись о клиенте
        cursor.execute('''
            INSERT INTO client (
                last_name, first_name, patronymic, phone, email, address, date_of_birth
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
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

        print(f"Создан клиент: {last_name} {first_name} (ID: {client_id})")

        # Генерируем уникальный username
        username = generate_unique_username(last_name, first_name, used_usernames)
        password_hash = "password123"  # В реальном приложении нужно хешировать!

        cursor.execute('''
            INSERT INTO user_login (client_id, username, password_hash)
            VALUES (?, ?, ?)
        ''', (client_id, username, password_hash))

        print(f"  — Создан логин: {username}")

        # Создаём счёт для клиента с балансом от 10 000 до 100 000 руб.
        balance = round(random.uniform(10000, 100000), 2)
        account_number = f"ACC-{random.randint(100000, 999999)}"

        cursor.execute('''
            INSERT INTO account (
                client_id, account_number, balance, currency, status, interest_rate
            ) VALUES (?, ?, ?, 'RUB', 'active', 0.0)
        ''', (client_id, account_number, balance))
        account_id = cursor.lastrowid

        print(f"  — Создан аккаунт: {account_number} (баланс: {balance} руб.)")

        # Добавляем несколько транзакций для каждого счёта
        num_transactions = random.randint(2, 5)
        for _ in range(num_transactions):
            transaction_type = random.choice(['deposit', 'withdrawal'])
            amount = round(random.uniform(500, 15000), 2)

            if transaction_type == 'withdrawal':
                # Проверяем, что не снимаем больше, чем есть на счёте
                if amount > balance:
                    amount = balance / 2
                balance -= amount
            else:
                balance += amount

            cursor.execute('''
                INSERT INTO account_transaction (account_id, transaction_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (account_id, transaction_type, amount, f"Тестовая {transaction_type}"))

    # Создаём несколько кредитов
    for _ in range(3):
        client_id = random.choice(client_ids)
        amount = round(random.uniform(50000, 200000), 2)
        interest_rate = round(random.uniform(8.0, 15.0), 1)

        start_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=random.randint(365, 1095))).strftime('%Y-%m-%d')


        cursor.execute('''
            INSERT INTO loan (client_id, amount, remaining_amount, interest_rate, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (client_id, amount, amount, interest_rate, start_date, end_date))

        print(f"Создан кредит для клиента {client_id} на сумму {amount} руб.")


    # Создаём несколько депозитов
    for _ in range(3):
        client_id = random.choice(client_ids)
        amount = round(random.uniform(30000, 150000), 2)
        interest_rate = round(random.uniform(4.0, 8.0), 1)

        start_date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=random.randint(365, 730))).strftime('%Y-%m-%d')

        cursor.execute('''
            INSERT INTO deposit (client_id, amount, interest_rate, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (client_id, amount, interest_rate, start_date, end_date))

        print(f"Создан депозит для клиента {client_id} на сумму {amount} руб. (ставка: {interest_rate}%, срок: {start_date} – {end_date})")

    # Сохраняем все изменения
    conn.commit()
    conn.close()

    print(f"\nБаза данных успешно заполнена! Создано {len(client_ids)} клиентов.")
    print("Данные готовы к использованию в банковской системе.")

if __name__ == "__main__":
    main()
