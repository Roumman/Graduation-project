import sqlite3

def clear_all_tables():
    """Полная очистка всех таблиц в базе данных"""
    conn = sqlite3.connect('Bank_DB.db')
    cursor = conn.cursor()

    tables = [
        'account_transaction',
        'loan',
        'deposit',
        'account',
        'user_login',
        'client'
    ]

    print("Начинаем очистку базы данных...")

    # Отключаем проверку внешних ключей для безопасного удаления
    cursor.execute("PRAGMA foreign_keys = OFF")

    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Таблица {table} очищена")
        except sqlite3.Error as e:
            print(f"Ошибка при очистке таблицы {table}: {e}")

    # Включаем проверку внешних ключей обратно
    cursor.execute("PRAGMA foreign_keys = ON")

    conn.commit()
    conn.close()
    print("Все таблицы успешно очищены!")

if __name__ == "__main__":
    clear_all_tables()