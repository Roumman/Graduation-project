import sqlite3

def populate_training_tasks():
    conn = sqlite3.connect('Trainer_DB.db')
    cursor = conn.cursor()

    # ОЧИЩАЕМ ТАБЛИЦУ ПЕРЕД ЗАПОЛНЕНИЕМ
    cursor.execute("DELETE FROM training_tasks")


    # === БАЗОВЫЙ УРОВЕНЬ (Basic) ===

    # Категория: SELECT
    basic_select_tasks = [
        ('basic', 'SELECT',
         'Вывести список всех клиентов (фамилию и имя) в алфавитном порядке',
         'SELECT last_name, first_name FROM client ORDER BY last_name;',
         'Используйте ORDER BY для сортировки'),

        ('basic', 'SELECT',
         'Показать баланс счёта с account_id = 5',
         'SELECT balance FROM account WHERE account_id = 5;',
         'Добавьте условие WHERE для фильтрации по ID'),

        ('basic', 'SELECT',
         'Найти всех клиентов, у которых в поле city указано «Москва»',
         "SELECT * FROM client WHERE city = 'Moscow';",
         'Используйте оператор = для точного совпадения')
    ]

    # Категория: INSERT
    basic_insert_tasks = [
        ('basic', 'INSERT',
         'Добавить нового клиента с client_id = 100, фамилией «Петров», именем «Сергей» и городом «Санкт-Петербург»',
         "INSERT INTO client (client_id, last_name, first_name, city) VALUES (100, 'Петров', 'Сергей', 'Санкт-Петербург');",
         'Укажите все необходимые поля в INSERT'),

        ('basic', 'INSERT',
         'Создать новый счёт с account_id = 200, принадлежащий клиенту с client_id = 10, с начальным балансом 10 000 и статусом «active»',
         "INSERT INTO account (account_id, client_id, balance, status) VALUES (200, 10, 10000, 'active');",
         'Не забудьте указать все обязательные поля'),

        ('basic', 'INSERT',
         'Записать новую транзакцию списания (debit) со счёта account_id = 15 на сумму 500 рублей',
         "INSERT INTO transaction (account_id, amount, type) VALUES (15, 500, 'debit');",
         'Тип транзакции — debit/credit')
    ]

    # Категория: UPDATE
    basic_update_tasks = [
        ('basic', 'UPDATE',
         'Повысить баланс счёта с account_id = 3 на 1 000 рублей',
         'UPDATE account SET balance = balance + 1000 WHERE account_id = 3;',
         'Используйте арифметическую операцию в SET'),

        ('basic', 'UPDATE',
         'Изменить статус счёта с account_id = 7 на «inactive»',
         "UPDATE account SET status = 'inactive' WHERE account_id = 7;",
         'Обновите значение поля status'),

        ('basic', 'UPDATE',
         'Обновить город для клиента с client_id = 4 на «Казань»',
         "UPDATE client SET city = 'Казань' WHERE client_id = 4;",
         'Измените значение поля city')
    ]

    # === ПРОДВИНУТЫЙ УРОВЕНЬ (Advanced) ===

    # Категория: JOIN
    advanced_join_tasks = [
        ('advanced', 'JOIN',
         'Вывести ФИО клиента и сумму его счетов (используя SUM и JOIN)',
         'SELECT c.last_name, c.first_name, SUM(a.balance) AS total_balance FROM client c JOIN account a ON c.client_id = a.client_id GROUP BY c.client_id;',
         'Соедините таблицы client и account, используйте GROUP BY'),

        ('advanced', 'JOIN',
         'Показать список счетов и имена их владельцев (соединение client и account)',
         'SELECT a.account_id, a.balance, c.last_name, c.first_name FROM account a JOIN client c ON a.client_id = c.client_id;',
         'Используйте INNER JOIN для связи таблиц'),

        ('advanced', 'JOIN',
         'Найти клиентов, у которых нет счетов (использовать LEFT JOIN и проверку на NULL)',
         'SELECT c.* FROM client c LEFT JOIN account a ON c.client_id = a.client_id WHERE a.account_id IS NULL;',
         'LEFT JOIN вернёт всех клиентов, даже без счетов')
    ]

    # Категория: AGGREGATE
    advanced_aggregate_tasks = [
        ('advanced', 'AGGREGATE',
         'Посчитать средний баланс по всем активным счетам',
         "SELECT AVG(balance) FROM account WHERE status = 'active';",
         'Используйте функцию AVG() с условием WHERE'),

        ('advanced', 'AGGREGATE',
         'Подсчитать, сколько счетов у каждого клиента (сгруппировать по client_id)',
         'SELECT client_id, COUNT(*) AS account_count FROM account GROUP BY client_id;',
         'Используйте COUNT() и GROUP BY'),

        ('advanced', 'AGGREGATE',
         'Найти максимальный и минимальный баланс среди всех счетов',
         'SELECT MAX(balance) AS max_balance, MIN(balance) AS min_balance FROM account;',
         'MAX() и MIN() можно использовать вместе')
    ]

    # Категория: SUBQUERY
    advanced_subquery_tasks = [
        ('advanced', 'SUBQUERY',
         'Вывести клиентов, у которых баланс счёта выше среднего по всем счетам',
         'SELECT c.* FROM client c WHERE c.client_id IN (SELECT client_id FROM account WHERE balance > (SELECT AVG(balance) FROM account));',
         'Внутренний подзапрос вычисляет средний баланс'),

        ('advanced', 'SUBQUERY',
         'Показать счета, по которым не было транзакций (использовать NOT IN)',
         'SELECT * FROM account WHERE account_id NOT IN (SELECT account_id FROM transaction);',
         'NOT IN исключает записи, найденные во внутреннем запросе'),

        ('advanced', 'SUBQUERY',
         'Найти клиентов, которые совершали транзакции (использовать EXISTS)',
         'SELECT * FROM client c WHERE EXISTS (SELECT 1 FROM transaction t WHERE t.account_id IN (SELECT account_id FROM account a WHERE a.client_id = c.client_id));',
         'EXISTS проверяет наличие записей во внутреннем запросе')
    ]

    # === ЭКСПЕРТНЫЙ УРОВЕНЬ (Expert) ===

    # Категория: TRIGGER
    expert_trigger_tasks = [
        ('expert', 'TRIGGER',
         'Создать триггер, который при обновлении баланса счёта записывает старую и новую сумму в таблицу лога balance_log',
         '''CREATE TRIGGER log_balance_change
AFTER UPDATE ON account
FOR EACH ROW
BEGIN
    INSERT INTO balance_log (account_id, old_balance, new_balance)
    VALUES (NEW.account_id, OLD.balance, NEW.balance);
END;''',
         'Используйте OLD и NEW для доступа к старым/новым значениям')
    ]

    # Категория: VIEW
    expert_view_tasks = [
        ('expert', 'VIEW',
         'Создать представление active_accounts_view, которое показывает только активные счета (status = \'active\') с ФИО владельца',
         '''CREATE VIEW active_accounts_view AS
SELECT a.account_id, a.balance, c.last_name, c.first_name
FROM account a
JOIN client c ON a.client_id = c.client_id
WHERE a.status = 'active';''',
         'CREATE VIEW создаёт виртуальную таблицу')
    ]

    # Категория: ANALYSIS
    expert_analysis_tasks = [
        ('expert', 'ANALYSIS',
         'Найти клиентов, которые не совершали транзакций более 6 месяцев',
         '''SELECT c.*
FROM client c
LEFT JOIN transaction t ON c.client_id = (SELECT client_id FROM account WHERE account_id = t.account_id)
WHERE t.transaction_date < DATE('now', '-6 months') OR t.transaction_date IS NULL;''',
         'Используйте DATE() для работы с датами'),

        ('expert', 'ANALYSIS',
         'Вывести топ‑3 клиентов с наибольшим суммарным балансом на счетах',
         '''SELECT c.client_id, c.last_name, SUM(a.balance) AS total_balance
FROM client c
JOIN account a ON c.client_id = a.client_id
GROUP BY c.client_id
ORDER BY total_balance DESC
LIMIT 3;''',
         'GROUP BY + ORDER BY + LIMIT для рейтинга'),

        ('expert', 'ANALYSIS',
         'Определить, есть ли клиенты с отрицательным балансом на каком‑либо из своих счетов',
         '''SELECT DISTINCT c.client_id, c.last_name
FROM client c
JOIN account a ON c.client_id = a.client_id
WHERE a.balance < 0;''',
         'JOIN свяжет клиентов с их счетами, WHERE отфильтрует отрицательные балансы')
    ]


    # СОБИРАЕМ ВСЕ ЗАДАНИЯ В ОДИН СПИСОК
    all_tasks = (
        basic_select_tasks + basic_insert_tasks + basic_update_tasks +
        advanced_join_tasks + advanced_aggregate_tasks + advanced_subquery_tasks +
        expert_trigger_tasks + expert_view_tasks + expert_analysis_tasks
    )


    # ЗАПОЛНЯЕМ БАЗУ
    for task in all_tasks:
        cursor.execute('''
            INSERT INTO training_tasks (level_type, task_category, task_description, correct_query, hint)
            VALUES (?, ?, ?, ?, ?)
        ''', task)

    conn.commit()
    conn.close()
    print("База данных успешно заполнена заданиями по уровням сложности!")

if __name__ == "__main__":
    populate_training_tasks()