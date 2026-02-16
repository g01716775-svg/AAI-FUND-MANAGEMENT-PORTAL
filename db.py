# models/db.py
import mysql.connector
from mysql.connector import Error # This import is correct
from contextlib import contextmanager
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_connection():
    """
    Update credentials below as needed.
    For production use environment variables or a secret manager.
    """
    try:
        conn = mysql.connector.connect( # pragma: no cover
               host=os.getenv("DB_HOST", "localhost"),
               user=os.getenv("DB_USER", "root"),
               password=os.getenv("DB_PASSWORD", ""),
               database=os.getenv("DB_NAME", "aai_funds")
        )

        return conn
    except Error as e:
        raise RuntimeError(f"Database connection error: {e}")

@contextmanager
def get_cursor(dictionary=False):
    """
    Database cursor context manager to handle connection and cleanup.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=dictionary)
        yield cursor, conn
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def add_dashboard_refresh_column():
    """
    Adds the `dashboard_refresh` column to the `stations` table if it does not already exist.
    """
    try:
        with get_cursor() as (cursor, conn):
            # Check if the column exists
            cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'stations' AND COLUMN_NAME = 'dashboard_refresh';
            """)
            column_exists = cursor.fetchone()[0] > 0

            if not column_exists:
                logging.info("Adding 'dashboard_refresh' column to 'stations' table.")
                cursor.execute("""
                ALTER TABLE stations
                ADD COLUMN dashboard_refresh BOOLEAN DEFAULT FALSE;
                """)
                conn.commit()
                logging.info("'dashboard_refresh' column added successfully.")
            else:
                logging.info("'dashboard_refresh' column already exists.")
    except Error as e:
        logging.error(f"Failed to add 'dashboard_refresh' column: {e}")
        raise
