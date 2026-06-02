import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from DataBase_Trainer import DataBaseTrainer


class TrainerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SQL Тренажёр для банковской системы")
        self.root.geometry("1200x700")
        self.trainer = DataBaseTrainer()
        self.current_user_id = None
        self.current_task = None
        self.show_login_screen()

    def clear_screen(self):
        """Очистка экрана — удаление всех виджетов"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        """Экран входа в тренажёр"""
        self.clear_screen()
        tk.Label(self.root, text="Вход в SQL Тренажёр",
                  font=("Arial", 16, "bold")).pack(pady=30)

        tk.Label(self.root, text="Логин:").pack()
        self.username_entry = tk.Entry(self.root, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Пароль:").pack()
        self.password_entry = tk.Entry(self.root, show="*", width=30)
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Войти", command=self.process_login,
              bg="lightgreen", width=15).pack(pady=10)
        tk.Button(self.root, text="Регистрация", command=self.show_register_screen,
              bg="skyblue", width=15).pack(pady=5)

    def show_register_screen(self):
        """Экран регистрации"""
        self.clear_screen()
        tk.Label(self.root, text="Регистрация нового пользователя",
                  font=("Arial", 14, "bold")).pack(pady=20)

        tk.Label(self.root, text="Логин:").pack()
        self.reg_username_entry = tk.Entry(self.root, width=30)
        self.reg_username_entry.pack(pady=5)

        tk.Label(self.root, text="Пароль:").pack()
        self.reg_password_entry = tk.Entry(self.root, show="*", width=30)
        self.reg_password_entry.pack(pady=5)

        tk.Label(self.root, text="Подтвердите пароль:").pack()
        self.confirm_password_entry = tk.Entry(self.root, show="*", width=30)
        self.confirm_password_entry.pack(pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Зарегистрироваться", command=self.process_registration,
              bg="lightblue", width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Назад", command=self.show_login_screen,
              width=12).pack(side="left", padx=5)

    def process_registration(self):
        """Обработка регистрации"""
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        if password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают!")
            return

        if self.trainer.register_user(username, password):
            messagebox.showinfo("Успех", "Регистрация прошла успешно! Теперь войдите в систему.")
            self.show_login_screen()
        else:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")


    def process_login(self):
        """Обработка входа в тренажёр"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        user_id = self.trainer.authenticate_user(username, password)
        if user_id:
            self.current_user_id = user_id
            self.show_main_menu()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def get_username(self):
        """Получение имени пользователя из БД"""
        cursor = self.trainer.trainer_conn.cursor()
        cursor.execute('''
        SELECT username FROM trainer_users WHERE user_id = ?
        ''', (self.current_user_id,))
        result = cursor.fetchone()
        return result[0] if result else "Пользователь"


    def show_main_menu(self):
        """Главное меню тренажёра"""
        self.clear_screen()
        tk.Label(self.root, text="Главное меню SQL Тренажёра",
                  font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(self.root, text=f"Добро пожаловать, {self.get_username()}!",
                  font=("Arial", 12)).pack(pady=10)

        # Кнопки выбора уровня
        levels_frame = tk.LabelFrame(self.root, text="Выберите уровень сложности")
        levels_frame.pack(padx=20, pady=10, fill="x")

        ttk.Button(levels_frame, text="Базовый уровень",
              command=lambda: self.show_category_selection('basic')).pack(pady=5, padx=10, anchor="w")
        ttk.Button(levels_frame, text="Продвинутый уровень",
              command=lambda: self.show_category_selection('advanced')).pack(pady=5, padx=10, anchor="w")
        ttk.Button(levels_frame, text="Экспертный уровень",
              command=lambda: self.show_category_selection('expert')).pack(pady=5, padx=10, anchor="w")

        # Кнопка просмотра прогресса
        progress_btn = ttk.Button(self.root, text="Мой прогресс",
                              command=self.show_progress)
        progress_btn.pack(pady=10)

        # Кнопка выхода
        logout_btn = ttk.Button(self.root, text="Выйти",
                             command=self.logout)
        logout_btn.pack(pady=5)
    
    def show_category_selection(self, level_type):
        self.clear_screen()
        tk.Label(self.root, text=f"Уровень: {level_type.capitalize()}",
                 font=("Arial", 14, "bold")).pack(pady=20)
    
        categories_frame = tk.LabelFrame(self.root, text="Выберите категорию заданий")
        categories_frame.pack(padx=20, pady=10, fill="both", expand=True)
    
        if level_type == 'basic':
            categories = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        elif level_type == 'advanced':
            categories = ['JOIN', 'AGGREGATE', 'SUBQUERY', 'FILTERING & ORDER']
        elif level_type == 'expert':
            categories = ['TRIGGER', 'VIEW', 'PROCEDURE', 'OPTIMIZATION', 'ANALYSIS']
    
        for category in categories:
            ttk.Button(categories_frame, text=category,
                       command=lambda cat=category: self.start_training(level_type, cat)).pack(pady=5, padx=10, fill="x")
    
        back_btn = ttk.Button(self.root, text="Назад в меню",
                             command=self.show_main_menu)
        back_btn.pack(pady=10)


    def start_training(self, level_type, category):
        """Начало тренировки — получение задания"""
        self.current_task = self.trainer.get_random_task(level_type, category)
        if not self.current_task:
            messagebox.showerror("Ошибка", "Задания для этой категории пока нет!")
            return
        self.show_task_screen()


    def display_db_schema(self, parent):
        """Отображение схемы базы данных в левой части"""
        # Получаем структуру таблиц из Bank_DB
        tables_info = self.get_bank_db_schema()

        for table_name, columns in tables_info.items():
            table_frame = tk.LabelFrame(parent, text=table_name, width=380)
            table_frame.pack(fill="x", padx=5, pady=2)
            table_frame.pack_propagate(False)  # Фиксированная ширина

            for col_info in columns:
                col_text = f"{col_info['name']} ({col_info['type']})"
                if col_info.get('primary_key'):
                    col_text += " [PK]"
                elif col_info.get('foreign_key'):
                    col_text += " [FK]"

                tk.Label(table_frame, text=col_text, anchor="w").pack(fill="x")

    def get_bank_db_schema(self):
        """Получение структуры таблиц из Bank_DB"""
        schema = {}
        try:
            cursor = self.trainer.bank_conn.cursor()
            # Получаем список таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                # Получаем информацию о колонках
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                schema[table_name] = []

                for col in columns_info:
                    col_dict = {
                'name': col[1],
                'type': col[2],
                'primary_key': col[5] == 1
            }
            schema[table_name].append(col_dict)
        except Exception as e:
            print(f"Ошибка получения схемы БД: {e}")
            # Схема по умолчанию, если не удалось получить из БД
            schema = {
                "client": [
                    {"name": "client_id", "type": "INTEGER", "primary_key": True},
                    {"name": "last_name", "type": "TEXT"},
                    {"name": "first_name", "type": "TEXT"},
            {"name": "phone", "type": "TEXT"}
        ],
        "account": [
            {"name": "account_id", "type": "INTEGER", "primary_key": True},
            {"name": "client_id", "type": "INTEGER", "foreign_key": True},
            {"name": "balance", "type": "REAL"},
            {"name": "status", "type": "TEXT"}
        ]
        }
        return schema

    def generate_ai_task_description(self, task):
        """Генерация описания задания от ИИ"""
        base_desc = task['description']
        ai_enhancement = "\n\n💡 Подсказка от ИИ: Попробуйте использовать следующие таблицы и колонки:\n"

        # Анализируем запрос, чтобы понять, какие таблицы нужны
        correct_query = task['correct_query'].lower()
        if 'client' in correct_query:
            ai_enhancement += "- Таблица client: client_id, last_name, first_name, phone\n"
        if 'account' in correct_query:
            ai_enhancement += "- Таблица account: account_id, client_id, balance, status\n"

        return base_desc + ai_enhancement

    def show_task_screen(self):
        """Экран задания с схемой БД слева и рабочей областью справа"""
        self.clear_screen()
        task = self.current_task

        # Основной фрейм с разделением на две части
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Левая часть — схема БД
        left_frame = tk.LabelFrame(main_frame, text="Схема базы данных Bank_DB", width=400)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)  # Фиксированная ширина

        # Отображение схемы БД
        self.display_db_schema(left_frame)

        # Правая часть — рабочая область
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        # Заголовок задания
        tk.Label(right_frame, text=f"Задание ({task['level_type'].capitalize()} уровень)",
                  font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(right_frame, text=task['description'],
                  wraplength=600, justify="left").pack(pady=5, padx=10)

        # Верхняя часть правой области — задание от ИИ
        ai_task_frame = tk.LabelFrame(right_frame, text="Задание от ИИ")
        ai_task_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(ai_task_frame, text=self.generate_ai_task_description(task),
                  justify="left", wraplength=600).pack(padx=10, pady=5)

        # Поле для ввода SQL‑запроса
        query_frame = tk.LabelFrame(right_frame, text="Ваш SQL запрос")
        query_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.query_entry = scrolledtext.ScrolledText(query_frame, height=8, width=60)
        self.query_entry.pack(pady=5, padx=5, fill="both", expand=True)

        # Кнопки действий
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Проверить ответ",
              command=self.check_answer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Показать эталонное решение",
              command=self.show_correct_solution).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Подсказка",
              command=self.show_hint).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Пропустить",
              command=self.skip_task).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Назад к списку",
           command=self.go_back).pack(side="left", padx=5)

        # Область для вывода результатов
        self.result_text = tk.Text(right_frame, height=6, width=70, state="disabled")
        self.result_text.pack(pady=5, padx=10, fill="both")

    def go_back(self):
        """Возвращает пользователя в главное меню тренажёра"""
        self.clear_screen()  # Очищаем текущее окно от элементов задания
        self.show_main_menu()  # Вызываем метод отображения главного меню

    def check_answer(self):
        """Проверка ответа пользователя"""
        user_query = self.query_entry.get("1.0", "end-1c")
        if not user_query.strip():
            messagebox.showwarning("Предупреждение", "Введите SQL запрос!")
            return

        task = self.current_task
        is_correct = self.trainer.check_task_solution(user_query, task['correct_query'])


        # Выполняем запрос и показываем результат
        execution_result = self.trainer.safe_execute_query(user_query)

        self.display_result(execution_result, is_correct)


        if is_correct:
            # Обновляем прогресс
            self.trainer.update_progress(self.current_user_id,
                                   task['level_type'], task['task_category'])
            messagebox.showinfo("Правильно!", "Ответ верный! Прогресс обновлён.")
            self.start_training(task['level_type'], task['task_category'])  # Следующее задание

    def display_result(self, execution_result, is_correct):
        """Отображение результата выполнения запроса"""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")


        if execution_result['success']:
            if execution_result['results']:
                # Форматируем вывод результатов (первые 10 строк)
                output = "Результаты:\n"
                for row in execution_result['results'][:10]:
                    output += f"{row}\n"

                if len(execution_result['results']) > 10:
                    output += f"... и ещё {len(execution_result['results']) - 10} строк\n"
            else:
                output = "Запрос выполнен успешно, но вернул пустой результат.\n"
        else:
            # Ошибка выполнения запроса
            output = f"Ошибка выполнения: {execution_result['error']}\n"

        # Добавляем информацию о правильности ответа
        if is_correct:
            output += "\n✅ Ваш ответ ВЕРНЫЙ!"
        else:
            output += "\n❌ Ваш ответ НЕВЕРНЫЙ. Попробуйте ещё раз."

        self.result_text.insert("1.0", output)
        self.result_text.config(state="disabled")


    def show_correct_solution(self):
        """Показать эталонное решение от ИИ"""
        if self.current_task:
            solution = self.current_task['correct_query']
            explanation = self.current_task.get('explanation', 'Объяснение отсутствует.')

            solution_window = tk.Toplevel(self.root)
            solution_window.title("Эталонное решение")
            solution_window.geometry("600x400")

            tk.Label(solution_window, text="Правильный SQL запрос:",
                      font=("Arial", 12, "bold")).pack(pady=10)

            query_text = tk.Text(solution_window, height=6, width=70)
            query_text.pack(pady=5, padx=20, fill="both", expand=True)
            query_text.insert("1.0", solution)
            query_text.config(state="disabled")

            tk.Label(solution_window, text="Объяснение решения:",
                      font=("Arial", 12, "bold")).pack(pady=10)


            expl_text = tk.Text(solution_window, height=8, width=70)
            expl_text.pack(pady=5, padx=20, fill="both", expand=True)
            expl_text.insert("1.0", explanation)
            expl_text.config(state="disabled")

            close_btn = ttk.Button(solution_window, text="Закрыть",
                          command=solution_window.destroy)
            close_btn.pack(pady=10)

    def show_hint(self):
        """Показать подсказку к заданию"""
        if self.current_task and self.current_task.get('hint'):
            hint = self.current_task['hint']
            messagebox.showinfo("Подсказка", hint)
        else:
            messagebox.showinfo("Подсказка", "Для этого задания подсказки нет.")

    def skip_task(self):
        """Пропустить текущее задание"""
        messagebox.showinfo("Пропуск", "Задание пропущено. Загружается новое...")
        task = self.current_task
        self.start_training(task['level_type'], task['task_category'])


    def show_progress(self):
        """Показать прогресс пользователя"""
        self.clear_screen()
        tk.Label(self.root, text="Мой прогресс",
                  font=("Arial", 16, "bold")).pack(pady=20)

        progress_data = self.trainer.get_user_progress(self.current_user_id)

        if not progress_data:
            tk.Label(self.root, text="У вас пока нет выполненных заданий.",
                      font=("Arial", 12)).pack(pady=20)
            back_btn = ttk.Button(self.root, text="Назад в меню",
                        command=self.show_main_menu)
            back_btn.pack(pady=10)
            return

        # Создаём таблицу прогресса
        tree = ttk.Treeview(self.root, columns=('Уровень', 'Категория', 'Выполнено', 'Всего'), show='headings')
        tree.heading('Уровень', text='Уровень')
        tree.heading('Категория', text='Категория')
        tree.heading('Выполнено', text='Выполнено')
        tree.heading('Всего', text='Всего заданий')


        tree.column('Уровень', width=100)
        tree.column('Категория', width=150)
        tree.column('Выполнено', width=80)
        tree.column('Всего', width=80)

        for level_type, category, completed, total in progress_data:
            tree.insert('', 'end', values=(
                level_type.capitalize(),
                category,
                completed,
                total
            ))

        tree.pack(padx=20, pady=10, fill="both", expand=True)

        # Подсчёт общего прогресса
        total_completed = sum(item[2] for item in progress_data)
        total_tasks = sum(item[3] for item in progress_data)


        summary_text = f"Общий прогресс: {total_completed} из {total_tasks} заданий"
        tk.Label(self.root, text=summary_text,
                  font=("Arial", 12, "bold")).pack(pady=10)


        back_btn = ttk.Button(self.root, text="Назад в меню",
                      command=self.show_main_menu)
        back_btn.pack(pady=10)

    def logout(self):
        """Выход из системы"""
        self.current_user_id = None
        self.show_login_screen()


    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

    def __del__(self):
        """Деструктор — закрытие соединений при уничтожении объекта"""
        try:
            self.trainer.close_connections()
        except:
            pass

# Запуск приложения
if __name__ == "__main__":
    app = TrainerUI()
    app.run()
