import sqlite3
from config.settings import DB_PATH

class BatimentModel:
    """Modèle pour la table BATIMENT"""

    def __init__(self):
        self.db_path = DB_PATH

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Ajouter un bâtiment
    def add_batiment(self, nom, localisation=None, type_batiment=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO BATIMENT (nom, localisation, type_batiment)
            VALUES (?, ?, ?)
        """, (nom, localisation, type_batiment))
        conn.commit()
        conn.close()

    # Lister tous les bâtiments
    def get_all_batiments(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM BATIMENT")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # Récupérer un bâtiment par id
    def get_batiment_by_id(self, id_batiment):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM BATIMENT WHERE id_batiment=?", (id_batiment,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
