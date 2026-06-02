import sqlite3
import hashlib

def create_trainer_database():
    conn = sqlite3.connect('Trainer_DB.db')
    cursor = conn.cursor()

    # Таблица пользователей тренажёра
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trainer_users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица прогресса пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_progress (
        progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        level_type TEXT NOT NULL,  -- 'basic', 'advanced', 'expert'
        task_category TEXT NOT NULL, -- 'SELECT', 'INSERT', 'UPDATE', 'JOIN', etc.
        completed_tasks INTEGER DEFAULT 0,
        total_tasks INTEGER DEFAULT 5,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES trainer_users(user_id) ON DELETE CASCADE
    )
    ''')

    # Таблица заданий тренажёра
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS training_tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        level_type TEXT NOT NULL,  -- 'basic', 'advanced', 'expert'
        task_category TEXT NOT NULL,
        task_description TEXT NOT NULL,
        correct_query TEXT NOT NULL,
        hint TEXT,
        points INTEGER DEFAULT 10
    )
    ''')

    # Заполняем заданиями (пример для базового уровня)
    basic_tasks = [
        ('basic', 'SELECT', 'Вывести всех клиентов (фамилию, имя, телефон)',
         'SELECT last_name, first_name, phone FROM client', 'Используйте SELECT с нужными колонками'),
        ('basic', 'SELECT', 'Показать все активные счета с балансом больше 50000',
         'SELECT * FROM account WHERE status = "active" AND balance > 50000', 'Добавьте условие WHERE'),
        ('basic', 'INSERT', 'Добавить нового клиента в таблицу client',
         'INSERT INTO client (client_id, last_name, first_name, phone) VALUES (101, "Иванов", "Петр", "+79991234567")', 'Используйте INSERT INTO с указанием колонок и значений'),
        ('basic', 'UPDATE', 'Обновить телефон клиента с ID 1',
         'UPDATE client SET phone = "+79999999999" WHERE client_id = 1', 'Используйте UPDATE с условием WHERE'),
    ]

    for task in basic_tasks:
        cursor.execute('''
        INSERT OR IGNORE INTO training_tasks
        (level_type, task_category, task_description, correct_query, hint)
        VALUES (?, ?, ?, ?, ?)
        ''', task)

    conn.commit()
    conn.close()
    print("База данных тренажёра создана и заполнена!")

if __name__ == "__main__":
    create_trainer_database()
