import sqlite3
import os
from sqlite3 import Error

from config.settings import DB_PATH

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute("PRAGMA foreign_keys = ON;")
            self.connection.row_factory = sqlite3.Row
            return self.connection
        except Error as e:
            print(f"Erreur de connexion : {e}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=()):
        conn = self.connect()
        if conn is None: return False
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        except Error as e:
            print(f"Erreur SQL (Execute) : {e}")
            return False
        finally:
            self.close()

    def fetch_all(self, query, params=()):
        conn = self.connect()
        if conn is None: return []
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            print(f"Erreur SQL (Fetch All) : {e}")
            return []
        finally:
            self.close()