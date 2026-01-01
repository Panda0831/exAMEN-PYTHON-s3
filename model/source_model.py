import sqlite3
from config.settings import DB_PATH

class SourceModel:
    def __init__(self):
        self.db_path = DB_PATH
        
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_cout_kwh_by_source_name(self, nom_source):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT cout_kwh FROM SOURCE_ENERGIE WHERE nom_source = ?"
        cursor.execute(query, (nom_source,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result["cout_kwh"]
        return None
    
    def get_source_id_by_name(self, nom_source):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT id_source FROM SOURCE_ENERGIE WHERE nom_source = ?"
        cursor.execute(query, (nom_source,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result["id_source"]
        return None

    def get_all_sources(self):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT id_source, nom_source, cout_kwh, description FROM SOURCE_ENERGIE"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_source(self, nom_source, cout_kwh, description=None):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            INSERT INTO SOURCE_ENERGIE (nom_source, cout_kwh, description)
            VALUES (?, ?, ?)
        """
        try:
            cursor.execute(query, (nom_source, cout_kwh, description))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Error: Source with name '{nom_source}' already exists.")
            return None
        finally:
            conn.close()

    def update_source(self, id_source, nom_source, cout_kwh, description=None):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            UPDATE SOURCE_ENERGIE
            SET nom_source = ?, cout_kwh = ?, description = ?
            WHERE id_source = ?
        """
        try:
            cursor.execute(query, (nom_source, cout_kwh, description, id_source))
            conn.commit()
            return True, None # Success, no error message
        except sqlite3.IntegrityError:
            return False, f"Erreur: Une source nommée '{nom_source}' existe déjà."
        except sqlite3.Error as e:
            return False, f"Erreur de base de données lors de la modification de la source: {e}"
        finally:
            conn.close()

    def delete_source(self, id_source):
        conn = self.connect()
        cursor = conn.cursor()
        query = "DELETE FROM SOURCE_ENERGIE WHERE id_source = ?"
        try:
            cursor.execute(query, (id_source,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting source: {e}")
            return False
        finally:
            conn.close()