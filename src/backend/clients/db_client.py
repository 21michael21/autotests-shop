from typing import Dict
import psycopg2
import allure
import json


class DbClient:
    def __init__(self, config: Dict[str, any]) -> None:
        with allure.step("Подключение к базе данных"):
            try:
                self.conn = psycopg2.connect(**config)
                connection_info = {
                    "host": config.get("host"),
                    "port": config.get("port"),
                    "database": config.get("dbname"),
                    "user": config.get("user"),
                    "status": "connected",
                }
                allure.attach(
                    json.dumps(connection_info, indent=2),
                    "Информация о подключении к БД",
                    allure.attachment_type.JSON,
                )
            except psycopg2.Error as e:
                error_details = {
                    "error_type": "DatabaseConnectionError",
                    "error_message": str(e),
                    "config": {k: v for k, v in config.items() if k != "password"},
                }
                allure.attach(
                    json.dumps(error_details, indent=2),
                    "❌ Ошибка подключения к БД",
                    allure.attachment_type.JSON,
                )
                raise

    @allure.step("🗄️ Выполнение SQL запроса: {query}")
    def execute(self, query: str) -> None:
        with allure.step(f"📝 Выполнение SQL: {query}"):
            try:
                allure.attach(query, "SQL запрос", allure.attachment_type.TEXT)
                cur = self.conn.cursor()
                cur.execute(query)
                try:
                    result = cur.fetchall()
                    if result:
                        allure.attach(
                            json.dumps(result, indent=2, default=str),
                            "Результат запроса",
                            allure.attachment_type.JSON,
                        )
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
                allure.attach(
                    json.dumps(error_details, indent=2),
                    "❌ Ошибка выполнения SQL",
                    allure.attachment_type.JSON,
                )
                self.conn.rollback()
                raise

    @allure.step("🧹 Удаление пользователя и связанных данных")
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

    @allure.step("🧹 Очистка корзины пользователя")
    def delete_cart(self, username: str) -> None:
        with allure.step(f"🛒 Очистка корзины пользователя: {username}"):
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