import tkinter as tk
from tkinter import ttk, messagebox
import re

class BankUI:
    def __init__(self, bank_db, auth_manager):
        self.bank_db = bank_db
        self.auth_manager = auth_manager
        self.current_client_id = None

        # Создаём главное окно
        self.root = tk.Tk()
        self.root.title("Банковская система")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Запускаем стартовый экран
        self.show_login_screen()

    def clear_screen(self):
        """Очистка экрана — удаление всех виджетов"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        """Экран входа в систему"""
        self.clear_screen()
        tk.Label(self.root, text="Вход в банковскую систему",
                  font=("Arial", 16, "bold")).pack(pady=30)

        # Поле для логина
        tk.Label(self.root, text="Логин:").pack()
        self.username_entry = tk.Entry(self.root, width=30)
        self.username_entry.pack(pady=5)

        # Поле для пароля
        tk.Label(self.root, text="Пароль:").pack()
        self.password_entry = tk.Entry(self.root, show="*", width=30)
        self.password_entry.pack(pady=5)

        # Кнопки
        tk.Button(self.root, text="Войти", command=self.process_login,
                 bg="lightgreen", width=15).pack(pady=10)
        tk.Button(self.root, text="Регистрация", command=self.show_register_screen,
                 bg="skyblue", width=15).pack(pady=5)

    def process_login(self):
        """Обработка входа в систему"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        user_data = self.auth_manager.authenticate(username, password)
        if user_data:
            self.current_client_id = user_data['client_id']
            self.show_account_screen()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def show_register_screen(self):
        """Экран регистрации нового пользователя"""
        self.clear_screen()
        tk.Label(self.root, text="Регистрация нового пользователя",
                  font=("Arial", 14, "bold")).pack(pady=20)

        # Поля для ввода данных
        fields = [
            ("Фамилия:", "last_name"),
            ("Имя:", "first_name"),
            ("Отчество:", "patronymic"),
            ("Телефон (+7...):", "phone"),
            ("Email:", "email"),
            ("Адрес:", "address"),
            ("Дата рождения (ГГГГ-ММ-ДД):", "date_of_birth"),
            ("Логин:", "username"),
            ("Пароль:", "password")
        ]

        self.register_entries = {}
        for label_text, field_name in fields:
            tk.Label(self.root, text=label_text).pack()
            entry = tk.Entry(self.root, width=30, show="*" if field_name == "password" else "")
            entry.pack(pady=2)
            self.register_entries[field_name] = entry

        # Кнопки
        tk.Button(self.root, text="Зарегистрироваться", command=self.process_registration,
                 bg="lightblue", width=20).pack(pady=15)
        tk.Button(self.root, text="Назад", command=self.show_login_screen,
                 width=20).pack(pady=5)

    def process_registration(self):
        """Обработка регистрации нового пользователя с валидацией"""
        data = {}
        for field_name, entry in self.register_entries.items():
            data[field_name] = entry.get().strip()

        # Проверка обязательных полей
        required_fields = ['last_name', 'first_name', 'date_of_birth', 'username', 'password']
        for field in required_fields:
            if not data[field]:
                messagebox.showerror("Ошибка", f"Поле '{field}' обязательно для заполнения!")
                return

        # Валидация ФИО — только буквы и пробелы (русские)
        import re
        name_pattern = r'^[А-Яа-яЁё\s]+$'
        if not re.match(name_pattern, data['last_name']):
            messagebox.showerror("Ошибка", "Фамилия должна содержать только русские буквы!")
            return
        if not re.match(name_pattern, data['first_name']):
            messagebox.showerror("Ошибка", "Имя должно содержать только русские буквы!")
            return
        if data['patronymic'] and not re.match(name_pattern, data['patronymic']):
            messagebox.showerror("Ошибка", "Отчество должно содержать только русские буквы!")
            return

        # Валидация телефона (российский формат)
        phone_pattern = r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
        if data['phone'] and not re.match(phone_pattern, data['phone']):
            messagebox.showerror("Ошибка", "Неверный формат телефона! Пример: +79991234567")
            return

        # Проверка даты рождения (простая проверка формата)
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, data['date_of_birth']):
            messagebox.showerror("Ошибка", "Неверный формат даты рождения! Используйте ГГГГ-ММ-ДД")
            return

        try:
            # Регистрация пользователя
            client_id = self.auth_manager.register_user(data)
            messagebox.showinfo("Успех", "Регистрация прошла успешно! Теперь войдите в систему.")
            self.show_login_screen()
        except ValueError as e:
            messagebox.showerror("Ошибка регистрации", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при регистрации: {str(e)}")

    def show_account_screen(self):
        """Экран личного кабинета"""
        self.clear_screen()
        client_info = self.bank_db.get_client_info(self.current_client_id)

        tk.Label(self.root, text=f"Добро пожаловать, {client_info['last_name']} {client_info['first_name']}",
                  font=("Arial", 14, "bold")).pack(pady=20)

        # Отображение баланса
        balance = self.bank_db.get_balance(self.current_client_id)
        tk.Label(self.root, text=f"Баланс: {balance:.2f} руб.",
                  font=("Arial", 12), fg="green").pack(pady=10)

        # Кнопки операций
        tk.Button(self.root, text="Пополнить счёт", command=self.show_deposit,
                 bg="lightgreen", width=20, height=2).pack(pady=8)
        tk.Button(self.root, text="Снять наличные", command=self.show_withdraw,
                 bg="lightcoral", width=20, height=2).pack(pady=8)
        tk.Button(self.root, text="Перевод между счетами", command=self.show_transfer_screen,
                 bg="skyblue", width=20, height=2).pack(pady=8)
        tk.Button(self.root, text="История транзакций", command=self.show_transaction_history,
                 width=20, height=2).pack(pady=8)
        tk.Button(self.root, text="Выйти", command=self.logout,
                 width=20, height=2, bg="orange").pack(pady=8)

    def update_balance(self):
        """Обновление отображения баланса"""
        balance = self.bank_db.get_balance(self.current_client_id)
        # Ищем метку баланса и обновляем её текст
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label) and "Баланс:" in widget.cget("text"):
                widget.config(text=f"Баланс: {balance:.2f} руб.")
                break

    def show_deposit(self):
        """Экран пополнения счёта"""
        self.clear_screen()
        tk.Label(self.root, text="Пополнение счёта", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(self.root, text="Сумма пополнения:").pack()
        self.deposit_amount_entry = tk.Entry(self.root, width=30)
        self.deposit_amount_entry.pack(pady=5)

        tk.Button(self.root, text="Пополнить", command=self.process_deposit,
                 bg="lightgreen", width=15).pack(pady=10)
        tk.Button(self.root, text="Назад", command=self.show_account_screen,
                 width=15).pack(pady=5)

    def process_deposit(self):
        """Обработка пополнения счёта"""
        try:
            amount = float(self.deposit_amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительной!")
                return

            self.bank_db.deposit(self.current_client_id, amount)
            messagebox.showinfo("Успех", f"Счёт пополнен на {amount:.2f} руб.")
            self.update_balance()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму!")


    def show_withdraw(self):
        """Экран снятия наличных"""
        self.clear_screen()
        tk.Label(self.root, text="Снятие наличных", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(self.root, text="Сумма для снятия:").pack()
        self.withdraw_amount_entry = tk.Entry(self.root, width=30)
        self.withdraw_amount_entry.pack(pady=5)

        tk.Button(self.root, text="Снять", command=self.process_withdraw,
                 bg="lightcoral", width=15).pack(pady=10)
        tk.Button(self.root, text="Назад", command=self.show_account_screen,
                 width=15).pack(pady=5)


    def process_withdraw(self):
        """Обработка снятия наличных"""
        try:
            amount = float(self.withdraw_amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительной!")
                return

            success = self.bank_db.withdraw(self.current_client_id, amount)
            if success:
                messagebox.showinfo("Успех", f"Снятие на сумму {amount:.2f} руб. выполнено!")
                self.update_balance()
            else:
                messagebox.showerror("Ошибка", "Недостаточно средств на счёте!")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму!")


    def show_transfer_screen(self):
        """Экран перевода между счетами"""
        self.clear_screen()
        tk.Label(self.root, text="Перевод между счетами", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(self.root, text="ID получателя:").pack()
        self.transfer_to_id_entry = tk.Entry(self.root, width=30)
        self.transfer_to_id_entry.pack(pady=5)

        tk.Label(self.root, text="Сумма перевода:").pack()
        self.transfer_amount_entry = tk.Entry(self.root, width=30)
        self.transfer_amount_entry.pack(pady=5)

        tk.Button(self.root, text="Перевести", command=self.process_transfer,
                 bg="skyblue", width=15).pack(pady=10)
        tk.Button(self.root, text="Назад", command=self.show_account_screen,
                 width=15).pack(pady=5)

    def process_transfer(self):
        """Обработка перевода между счетами"""
        try:
            to_client_id = int(self.transfer_to_id_entry.get())
            amount = float(self.transfer_amount_entry.get())

            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительной!")
                return

            success = self.bank_db.transfer(self.current_client_id, to_client_id, amount)
            if success:
                messagebox.showinfo("Успех", f"Перевод на сумму {amount:.2f} руб. выполнен!")
                self.update_balance()
            else:
                messagebox.showerror("Ошибка", "Ошибка при выполнении перевода! Проверьте ID получателя и баланс.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные данные!")

    def show_transaction_history(self):
        """Экран истории транзакций"""
        self.clear_screen()
        tk.Label(self.root, text="История транзакций", font=("Arial", 14, "bold")).pack(pady=15)

        # Получаем историю транзакций
        transactions = self.bank_db.get_transaction_history(self.current_client_id)

        if not transactions:
            tk.Label(self.root, text="Нет транзакций для отображения").pack(pady=20)
        else:
            # Создаём таблицу для отображения
            tree = ttk.Treeview(self.root, columns=('Тип', 'Сумма', 'Описание', 'Дата'), show='headings')
            tree.heading('Тип', text='Тип')
            tree.heading('Сумма', text='Сумма')
            tree.heading('Описание', text='Описание')
            tree.heading('Дата', text='Дата')

            for t in transactions:
                tree.insert('', 'end', values=(
                    t['type'],
            f"{t['amount']:.2f}",
            t['description'],
            t['timestamp']
        ))

            tree.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Button(self.root, text="Назад", command=self.show_account_screen,
                 width=15).pack(pady=10)

    def logout(self):
        """Выход из системы"""
        self.current_client_id = None
        self.show_login_screen()

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
