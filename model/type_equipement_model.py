import sqlite3
from config.settings import DB_PATH

class TypeEquipementModel:
    def __init__(self):
        self.db_path = DB_PATH
        
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_type_equipement_details(self, id_type):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT id_type, nom_type, consommation_theorique FROM TYPE_EQUIPEMENT WHERE id_type = ?"
        cursor.execute(query, (id_type,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_consommation_theorique_by_type_id(self, id_type):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT consommation_theorique FROM TYPE_EQUIPEMENT WHERE id_type = ?"
        cursor.execute(query, (id_type,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result["consommation_theorique"]
        return None
    
    def get_all_types_equipement(self):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT id_type, nom_type, consommation_theorique FROM TYPE_EQUIPEMENT"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_type_equipement(self, nom_type, consommation_theorique):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            INSERT INTO TYPE_EQUIPEMENT (nom_type, consommation_theorique)
            VALUES (?, ?)
        """
        try:
            cursor.execute(query, (nom_type, consommation_theorique))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Error adding type equipement: {e}")
            return None
        finally:
            conn.close()
