import sqlite3
from config.settings import DB_PATH

class EquipementModel:
    def __init__(self):
        self.db_path = DB_PATH
        
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_equipement_details(self, id_equipement):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT 
                e.id_equipement, e.nom_equipement, e.puissance_watt,
                te.nom_type, te.consommation_theorique as conso_theorique_type,
                b.nom as nom_batiment
            FROM EQUIPEMENT e
            JOIN TYPE_EQUIPEMENT te ON e.id_type = te.id_type
            JOIN BATIMENT b ON e.id_batiment = b.id_batiment
            WHERE e.id_equipement = ?
        """
        cursor.execute(query, (id_equipement,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_all_equipements(self):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT 
                e.id_equipement, e.nom_equipement, e.puissance_watt, e.id_type,
                te.nom_type, te.consommation_theorique as conso_theorique_type,
                b.nom as nom_batiment
            FROM EQUIPEMENT e
            JOIN TYPE_EQUIPEMENT te ON e.id_type = te.id_type
            JOIN BATIMENT b ON e.id_batiment = b.id_batiment
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_equipements_by_batiment(self, id_batiment):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT 
                e.id_equipement, e.nom_equipement, e.puissance_watt, e.id_type,
                te.nom_type, te.consommation_theorique as conso_theorique_type,
                b.nom as nom_batiment
            FROM EQUIPEMENT e
            JOIN TYPE_EQUIPEMENT te ON e.id_type = te.id_type
            JOIN BATIMENT b ON e.id_batiment = b.id_batiment
            WHERE e.id_batiment = ?
        """
        cursor.execute(query, (id_batiment,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_equipement(self, nom_equipement, puissance_watt, id_type, id_batiment):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            INSERT INTO EQUIPEMENT (nom_equipement, puissance_watt, id_type, id_batiment)
            VALUES (?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (nom_equipement, puissance_watt, id_type, id_batiment))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Error adding equipement: {e}")
            return None
        finally:
            conn.close()

    def update_equipement(self, id_equipement, nom_equipement, puissance_watt, id_type, id_batiment):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            UPDATE EQUIPEMENT
            SET nom_equipement = ?, puissance_watt = ?, id_type = ?, id_batiment = ?
            WHERE id_equipement = ?
        """
        try:
            cursor.execute(query, (nom_equipement, puissance_watt, id_type, id_batiment, id_equipement))
            conn.commit()
            return True, None # Success, no error message
        except sqlite3.IntegrityError as e:
            return False, f"Erreur: Un équipement nommé '{nom_equipement}' existe déjà dans ce bâtiment."
        except sqlite3.Error as e:
            return False, f"Erreur de base de données lors de la modification de l'équipement: {e}"
        finally:
            conn.close()

    def delete_equipement(self, id_equipement):
        conn = self.connect()
        cursor = conn.cursor()
        query = "DELETE FROM EQUIPEMENT WHERE id_equipement = ?"
        try:
            cursor.execute(query, (id_equipement,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting equipement: {e}")
            return False
        finally:
            conn.close()
