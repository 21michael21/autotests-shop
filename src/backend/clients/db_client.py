import json
from typing import Dict, Any

import allure
import psycopg2

from src.utils.allure_utils import attach_response_data, attach_error_details


class DatabaseClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conn = None
        self._connect()

    def _connect(self) -> None:
        with allure.step("Подключение к базе данных"):
            try:
                self.conn = psycopg2.connect(**self.config)
                connection_info = {
                    "host": self.config.get("host"),
                    "port": self.config.get("port"),
                    "database": self.config.get("dbname"),
                    "user": self.config.get("user"),
                    "status": "connected",
                }
                attach_response_data(connection_info, "Информация о подключении к БД")
            except psycopg2.Error as e:
                error_details = {
                    "error_type": "DatabaseConnectionError",
                    "error_message": str(e),
                    "config": {k: v for k, v in self.config.items() if k != "password"},
                }
                attach_error_details("DatabaseConnectionError", str(e), "database_connection", **error_details)
                raise

    def execute(self, query: str) -> None:
        with allure.step("Выполнение SQL запроса"):
            try:
                attach_response_data(query, "SQL запрос")
                cur = self.conn.cursor()
                cur.execute(query)
                try:
                    result = cur.fetchall()
                    if result:
                        attach_response_data(result, "Результат запроса")
                except psycopg2.ProgrammingError:
                    pass
                self.conn.commit()
                cur.close()
            except psycopg2.Error as e:
                error_details = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "sql_query": query,
                    "error_code": getattr(e, "pgcode", "N/A"),
                }
                attach_error_details(type(e).__name__, str(e), "sql_execution", **error_details)
                self.conn.rollback()
                raise

    @allure.step("Удаление пользователя и связанных данных")
    def delete_user(self, username: str) -> None:
        with allure.step(f"Удаление пользователя: {username}"):
            cart_items_query = f"""
            DELETE FROM cart_items
            WHERE cart_id IN (
                SELECT id FROM carts
                WHERE user_id = (
                    SELECT id FROM users
                    WHERE username = '{username}'
                )
            )
            """
            self.execute(cart_items_query)

            carts_query = f"""
            DELETE FROM carts
            WHERE user_id = (
                SELECT id FROM users
                WHERE username = '{username}'
            )
            """
            self.execute(carts_query)

            user_query = f"DELETE FROM users WHERE username = '{username}'"
            self.execute(user_query)

    @allure.step("Очистка корзины пользователя")
    def delete_cart(self, username: str) -> None:
        with allure.step(f"Очистка корзины пользователя: {username}"):
            cart_items_query = f"""
            DELETE FROM cart_items
            WHERE cart_id IN (
                SELECT id FROM carts
                WHERE user_id = (
                    SELECT id FROM users
                    WHERE username = '{username}'
                )
            )
            """
            self.execute(cart_items_query)

            carts_query = f"""
            DELETE FROM carts
            WHERE user_id = (
                SELECT id FROM users
                WHERE username = '{username}'
            )
            """
            self.execute(carts_query)

    def __del__(self):
        try:
            if hasattr(self, "conn") and self.conn:
                with allure.step("Закрытие соединения с БД"):
                    self.conn.close()
        except Exception:
            pass
