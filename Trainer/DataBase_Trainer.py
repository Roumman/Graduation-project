import sqlite3
import hashlib

class DataBaseTrainer:
    def __init__(self, bank_db_path="Bank_DB.db", trainer_db_path="Trainer_DB.db"):
        self.bank_conn = sqlite3.connect(bank_db_path)
        self.trainer_conn = sqlite3.connect(trainer_db_path)
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Проверяет и создаёт таблицы, если их нет"""
        cursor = self.trainer_conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainer_users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level_type TEXT NOT NULL,
            task_category TEXT NOT NULL,
            completed_tasks INTEGER DEFAULT 0,
            total_tasks INTEGER DEFAULT 5,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES trainer_users(user_id) ON DELETE CASCADE
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_type TEXT NOT NULL,
            task_category TEXT NOT NULL,
            task_description TEXT NOT NULL,
            correct_query TEXT NOT NULL,
            hint TEXT,
            points INTEGER DEFAULT 10
        )
        ''')
        self.trainer_conn.commit()

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        """Регистрация нового пользователя"""
        try:
            cursor = self.trainer_conn.cursor()
            password_hash = self.hash_password(password)
            cursor.execute('''
            INSERT INTO trainer_users (username, password_hash)
            VALUES (?, ?)
            ''', (username, password_hash))
            self.trainer_conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        cursor = self.trainer_conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute('''
        SELECT user_id FROM trainer_users
        WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_user_progress(self, user_id):
        """Получение прогресса пользователя"""
        cursor = self.trainer_conn.cursor()
        cursor.execute('''
        SELECT level_type, task_category, completed_tasks, total_tasks
        FROM user_progress
        WHERE user_id = ?
        ''', (user_id,))
        return cursor.fetchall()

    def update_progress(self, user_id, level_type, category):
        """Обновление прогресса пользователя"""
        cursor = self.trainer_conn.cursor()
        # Проверяем, есть ли запись для этой категории и уровня
        cursor.execute('''
        SELECT progress_id, completed_tasks
        FROM user_progress
        WHERE user_id = ? AND level_type = ? AND task_category = ?
        ''', (user_id, level_type, category))
        existing = cursor.fetchone()

        if existing:
            # Обновляем существующую запись
            new_completed = existing[1] + 1
            cursor.execute('''
            UPDATE user_progress
            SET completed_tasks = ?, last_updated = CURRENT_TIMESTAMP
            WHERE progress_id = ?
            ''', (new_completed, existing[0]))
        else:
            # Создаём новую запись
            cursor.execute('''
            INSERT INTO user_progress (user_id, level_type, task_category, completed_tasks)
            VALUES (?, ?, ?, 1)
            ''', (user_id, level_type, category))

        self.trainer_conn.commit()

    def get_random_task(self, level_type, task_category):
        """Получение случайного задания для уровня и категории"""
        cursor = self.trainer_conn.cursor()
        cursor.execute('''
        SELECT task_id, task_description, correct_query, hint
        FROM training_tasks
        WHERE level_type = ? AND task_category = ?
        ORDER BY RANDOM() LIMIT 1
        ''', (level_type, task_category))
        result = cursor.fetchone()

        if result:
            return {
                'task_id': result[0],
                'description': result[1],
                'correct_query': result[2],
                'hint': result[3],
                'level_type': level_type,
                'task_category': task_category
            }
        return None

    def check_task_solution(self, user_query, correct_query):
        """Проверка решения задачи (упрощённая проверка)"""
        # Убираем пробелы и приводим к нижнему регистру для сравнения
        clean_user = user_query.strip().lower().replace(' ', ' ')
        clean_correct = correct_query.strip().lower().replace(' ', ' ')

        # Базовая проверка — точное совпадение (с учётом нормализации)
        if clean_user == clean_correct:
            return True

        # Дополнительная проверка: проверяем, содержит ли запрос ключевые слова
        keywords = ['select', 'insert', 'update', 'delete', 'from', 'where', 'join']
        user_has_keywords = any(kw in clean_user for kw in keywords)
        correct_has_keywords = any(kw in clean_correct for kw in keywords)

        if user_has_keywords and correct_has_keywords:
            # Более гибкая проверка: сравниваем структуру запроса
            user_parts = set(part.strip() for part in clean_user.split() if part.strip())
            correct_parts = set(part.strip() for part in clean_correct.split() if part.strip())

            # Если большинство ключевых частей совпадают, считаем правильным
            common_parts = user_parts & correct_parts
            if len(common_parts) >= max(1, len(correct_parts) * 0.6):
                return True

        return False

    def safe_execute_query(self, query):
        """Безопасное выполнение пользовательского запроса"""
        try:
            # Проверяем, что запрос не содержит опасных команд
            dangerous_commands = ['drop', 'delete from', 'update', 'insert into']
            query_lower = query.lower()

            for cmd in dangerous_commands:
                if cmd in query_lower and 'where' not in query_lower:
                    return {
                'success': False,
                'error': 'Запрещена выполнение опасных команд без условия WHERE'
            }

            cursor = self.bank_conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []

            return {
                'success': True,
                'results': results,
                'columns': columns
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def close_connections(self):
        """Закрытие соединений с БД"""
        self.bank_conn.close()
        self.trainer_conn.close()
