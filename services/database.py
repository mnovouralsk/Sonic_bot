import sqlite3
import os
from typing import Optional

class DataBase:
    def __init__(self):
        self.DATABASE_NAME = "data/users.db"
        self.connection = self.create_connection()
        self.cursor = self.connection.cursor()

        if not self.table_exists():
            self.create_table()

    def __del__(self):
        """Закрываем соединение при удалении объекта."""
        self.close_connection()

    def table_exists(self) -> bool:
        """Проверяет, существует ли таблица users в базе данных."""
        check_table_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        self.cursor.execute(check_table_query)
        return self.cursor.fetchone() is not None

    def create_connection(self):
        """Создает соединение с базой данных SQLite."""
        if not os.path.exists(os.path.dirname(self.DATABASE_NAME)):
            os.makedirs(os.path.dirname(self.DATABASE_NAME))
        return sqlite3.connect(self.DATABASE_NAME)

    def create_table(self):
        """Создает таблицу users, если она не существует."""
        try:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_ID INTEGER NOT NULL UNIQUE,
                referrer_id INTEGER DEFAULT 0,
                time_sub INTEGER DEFAULT 0,
                signup VARCHAR DEFAULT 'setnickname'
            );
            """
            self.cursor.execute(create_table_query)
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")

    def add_user(self, user_id: int):
        """Добавляет нового пользователя в базу данных."""
        try:
            if self.user_exists(user_id):
                return  # Пользователь уже есть в базе
            self.cursor.execute("INSERT INTO users (USER_ID) VALUES (?)", (user_id,))
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")

    def user_exists(self, user_id: int) -> bool:
        """Проверяет, существует ли пользователь."""
        try:
            self.cursor.execute("SELECT 1 FROM users WHERE USER_ID = ?", (user_id,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(f"Ошибка при проверке существования пользователя: {e}")
            return False

    def get_signup(self, user_id: int) -> Optional[str]:
        """Возвращает поле signup пользователя."""
        try:
            self.cursor.execute("SELECT signup FROM users WHERE USER_ID = ?", (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка при получении signup: {e}")
            return None

    def set_signup(self, user_id: int, signup: str) -> bool:
        """Обновляет signup для пользователя."""
        try:
            self.cursor.execute("UPDATE users SET signup = ? WHERE USER_ID = ?", (signup, user_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении signup: {e}")
            return False

    def get_referrer_id(self, user_id: int) -> Optional[int]:
        """Получает referrer_id по user_id."""
        try:
            self.cursor.execute("SELECT referrer_id FROM users WHERE USER_ID = ?", (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Ошибка при получении referrer_id: {e}")
            return 0

    def set_referrer_id(self, user_id: int, referrer_id: int) -> bool:
        """Обновляет referrer_id по user_id."""
        try:
            self.cursor.execute("UPDATE users SET referrer_id = ? WHERE USER_ID = ?", (referrer_id, user_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении referrer_id: {e}")
            return False

    def get_user_by_referrer(self, referrer_id: int) -> int | None:
        """Возвращает user_id первого найденного пользователя с указанным referrer_id, либо None, если такого нет."""
        try:
            self.cursor.execute("SELECT USER_ID FROM users WHERE referrer_id = ? LIMIT 1", (referrer_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка при получении пользователя по referrer_id {referrer_id}: {e}")
            return None


    def close_connection(self):
        """Закрывает соединение с базой данных."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}")
