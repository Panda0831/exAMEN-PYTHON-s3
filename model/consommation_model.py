import sqlite3
from config.settings import DB_PATH

class ConsommationModel:
    def __init__(self):
        self.db_path = DB_PATH
        
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    def add_consommation (self, id_equipement, id_source, duree_minutes, energie_kwh, date_heure=None):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            INSERT INTO CONSOMMATION
            (id_equipement, id_source, date_heure, duree_minutes, energie_kwh)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (id_equipement, id_source, date_heure, duree_minutes, energie_kwh))
            conn.commit()
            return True, None
        except sqlite3.IntegrityError as e:
            return False, f"Erreur d'intégrité lors de l'ajout de consommation: {e}"
        except sqlite3.Error as e:
            return False, f"Erreur de base de données lors de l'ajout de consommation: {e}"
        finally:
            conn.close()
        
    def get_all_consommation(self):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT
                c.id_conso,
                c.id_equipement,
                c.id_source,
                c.date_heure,
                c.duree_minutes,
                c.energie_kwh,
                s.nom_source,
                e.nom_equipement,
                b.nom AS batiment
            FROM CONSOMMATION c
            JOIN SOURCE_ENERGIE s ON c.id_source = s.id_source
            JOIN EQUIPEMENT e ON c.id_equipement = e.id_equipement
            JOIN BATIMENT b ON e.id_batiment = b.id_batiment
            ORDER BY c.date_heure
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_consommation_by_source(self, nom_source):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT date_heure, energie_kwh
            FROM CONSOMMATION c
            JOIN SOURCE_ENERGIE s ON c.id_source = s.id_source
            WHERE s.nom_source = ?
            ORDER BY date_heure
        """

        cursor.execute(query, (nom_source,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_consommation_entre_dates(self, date_debut, date_fin):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT date_heure, energie_kwh
            FROM CONSOMMATION
            WHERE date_heure BETWEEN ? AND ?
            ORDER BY date_heure
        """

        cursor.execute(query, (date_debut, date_fin))
        rows = cursor.fetchall()
        conn.close()
        return [(row["date_heure"], row["energie_kwh"]) for row in rows]

    def get_consommation_by_building(self, building_id):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT
                c.id_conso,
                c.id_equipement,
                c.id_source,
                c.date_heure,
                c.duree_minutes,
                c.energie_kwh,
                s.nom_source,
                e.nom_equipement,
                b.nom AS batiment
            FROM CONSOMMATION c
            JOIN SOURCE_ENERGIE s ON c.id_source = s.id_source
            JOIN EQUIPEMENT e ON c.id_equipement = e.id_equipement
            JOIN BATIMENT b ON e.id_batiment = b.id_batiment
            WHERE b.id_batiment = ?
            ORDER BY c.date_heure
        """
        cursor.execute(query, (building_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]    
    def get_consommation_by_equipement(self, id_equipement):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT date_heure, energie_kwh
            FROM CONSOMMATION
            WHERE id_equipement = ?
            ORDER BY date_heure
        """

        cursor.execute(query, (id_equipement,))
        rows = cursor.fetchall()
        conn.close()

        return [(row["date_heure"], row["energie_kwh"]) for row in rows]