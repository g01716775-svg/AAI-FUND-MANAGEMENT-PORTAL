# models/user_model.py
from models.db import get_cursor # This import is correct

class UserModel:

    @staticmethod
    def get_user_by_email(email: str):
        with get_cursor(dictionary=True) as (cursor, _):
            query = """
                SELECT user_id, name, designation, email, password_hash, role, department, station_id, station_name
                FROM users
                WHERE email = %s
                LIMIT 1
            """
            cursor.execute(query, (email,))
            return cursor.fetchone()

    @staticmethod
    def create_user(
        name: str,
        designation: str,
        email: str,
        password_hash: str,
        role: str,
        department: str,
        station_id: int = None,
        station_name: str = None
    ):
        with get_cursor() as (cursor, conn):
            query = """
                INSERT INTO users (name, designation, email, password_hash, role, department, station_id, station_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, designation, email, password_hash, role, department, station_id, station_name))
            conn.commit()
            return cursor.lastrowid
