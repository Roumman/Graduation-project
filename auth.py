import hashlib

class AuthManager:
    def __init__(self, bank_db):
        self.bank_db = bank_db

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username, password):
        """Аутентификация пользователя"""
        password_hash = self.hash_password(password)
        return self.bank_db.authenticate_with_password(username, password_hash)

    def register_user(self, data):
        """Регистрация нового пользователя с валидацией"""
        # Валидация телефона (российский формат)
        import re
        phone_pattern = r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
        if data['phone'] and not re.match(phone_pattern, data['phone'].strip()):
            raise ValueError("Неверный формат телефона! Пример: +79991234567")

        # Создание клиента
        client_id = self.bank_db.create_client(
            data['last_name'],
            data['first_name'],
            data.get('patronymic', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('address', ''),
            data['date_of_birth']
        )
        # Хеширование пароля
        password_hash = self.hash_password(data['password'])
        # Создание учётной записи
        self.bank_db.create_user_login(client_id, data['username'], password_hash)
        # Создание счёта
        self.bank_db.create_account(client_id)
        return client_id
