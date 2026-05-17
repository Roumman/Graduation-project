def apply_triggers(db_path="Bank_DB.db"):
    """Применение триггеров к базе данных"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Читаем и выполняем SQL‑скрипт с триггерами
    with open('triggers.sql', 'r', encoding='utf-8') as f:
        trigger_sql = f.read()
        cursor.executescript(trigger_sql)

    conn.commit()
    conn.close()
    print("Триггеры успешно применены к базе данных!")

# В основном скрипте после создания и заполнения БД:
if __name__ == "__main__":
    print("Создание базы данных банковской системы...")
    conn = create_bank_database()
    print("Заполнение базы данных тестовыми данными...")
    populate_database(conn)
    conn.close()

    print("Применение триггеров...")
    apply_triggers()
    print("База данных успешно создана, заполнена и настроена!")
