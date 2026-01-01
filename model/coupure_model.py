import sqlite3
from config.settings import DB_PATH
from datetime import datetime

class CoupureModel:
    def __init__(self):
        self.db_path = DB_PATH
        
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_coupure(self, id_batiment, debut_coupure, fin_coupure=None, cause=None):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            INSERT INTO COUPURE (id_batiment, debut_coupure, fin_coupure, cause)
            VALUES (?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (id_batiment, debut_coupure, fin_coupure, cause))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            return False, f"Erreur de base de données lors de l'ajout de la coupure: {e}"
        finally:
            conn.close()

    def update_coupure(self, id_coupure, id_batiment, debut_coupure, fin_coupure=None, cause=None):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            UPDATE COUPURE
            SET id_batiment = ?, debut_coupure = ?, fin_coupure = ?, cause = ?
            WHERE id_coupure = ?
        """
        try:
            cursor.execute(query, (id_batiment, debut_coupure, fin_coupure, cause, id_coupure))
            conn.commit()
            return True, None # Success
        except sqlite3.Error as e:
            return False, f"Erreur de base de données lors de la modification de la coupure: {e}"
        finally:
            conn.close()

    def delete_coupure(self, id_coupure):
        conn = self.connect()
        cursor = conn.cursor()
        query = "DELETE FROM COUPURE WHERE id_coupure = ?"
        try:
            cursor.execute(query, (id_coupure,))
            conn.commit()
            return True, None # Success
        except sqlite3.Error as e:
            return False, f"Erreur de base de données lors de la suppression de la coupure: {e}"
        finally:
            conn.close()


    def get_all_coupures(self):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT
                c.id_coupure,
                c.id_batiment,
                c.debut_coupure,
                c.fin_coupure,
                c.cause,
                b.nom AS nom_batiment
            FROM COUPURE c
            JOIN BATIMENT b ON c.id_batiment = b.id_batiment
            ORDER BY c.debut_coupure DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_current_coupures(self):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT
                c.id_coupure,
                c.id_batiment,
                c.debut_coupure,
                c.fin_coupure,
                c.cause,
                b.nom AS nom_batiment
            FROM COUPURE c
            JOIN BATIMENT b ON c.id_batiment = b.id_batiment
            WHERE c.fin_coupure IS NULL
            ORDER BY c.debut_coupure DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_coupures_by_period(self, date_debut, date_fin):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT
                c.id_coupure,
                c.id_batiment,
                c.debut_coupure,
                c.fin_coupure,
                c.cause,
                b.nom AS nom_batiment
            FROM COUPURE c
            JOIN BATIMENT b ON c.id_batiment = b.id_batiment
            WHERE c.debut_coupure BETWEEN ? AND ? OR c.fin_coupure BETWEEN ? AND ?
            ORDER BY c.debut_coupure DESC
        """
        cursor.execute(query, (date_debut, date_fin, date_debut, date_fin))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
