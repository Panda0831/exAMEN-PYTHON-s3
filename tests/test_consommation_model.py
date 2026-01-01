import unittest
import os
import sqlite3
from datetime import datetime, timedelta

from model.consommation_model import ConsommationModel
from config.settings import DB_PATH

class TestConsommationModel(unittest.TestCase):
    def setUp(self):
        self.model = ConsommationModel()
        # Ensure a clean state for adding new data
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        # Clean up any test data inserted
        self.cursor.execute("DELETE FROM CONSOMMATION WHERE energie_kwh = 99.99")
        self.conn.commit()
        self.conn.close()

    def test_add_consommation(self):
        # Use existing valid IDs from the seeded data
        id_equipement = 1 
        id_source = 1
        duree_minutes = 30
        energie_kwh = 99.99
        date_heure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.model.add_consommation(id_equipement, id_source, duree_minutes, energie_kwh, date_heure)

        # Verify insertion
        conn = self.model.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CONSOMMATION WHERE energie_kwh = ?", (energie_kwh,))
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result["id_equipement"], id_equipement)
        self.assertEqual(result["id_source"], id_source)
        self.assertEqual(result["duree_minutes"], duree_minutes)
        self.assertEqual(result["energie_kwh"], energie_kwh)
        # Note: SQLite stores datetime as TEXT, so exact string comparison might be needed or parse to datetime objects.
        # For simplicity, we'll check if the start of the string matches.
        self.assertTrue(result["date_heure"].startswith(date_heure[:16])) # Check up to minutes

    def test_get_all_consommation(self):
        all_conso = self.model.get_all_consommation()
        self.assertIsInstance(all_conso, list)
        self.assertGreater(len(all_conso), 0) # Expect some data from seed.sql
        # Check structure of one item
        first_item = all_conso[0]
        self.assertIn("id_conso", first_item)
        self.assertIn("date_heure", first_item)
        self.assertIn("energie_kwh", first_item)
        self.assertIn("nom_source", first_item)
        self.assertIn("nom_equipement", first_item)
        self.assertIn("batiment", first_item)

    def test_get_consommation_by_source(self):
        # Use a source from seed data
        nom_source = "JIRAMA"
        conso_by_source = self.model.get_consommation_by_source(nom_source)
        self.assertIsInstance(conso_by_source, list)
        self.assertGreater(len(conso_by_source), 0)
        for item in conso_by_source:
            self.assertIn("date_heure", item)
            self.assertIn("energie_kwh", item)
        
        # Test a non-existent source
        conso_non_existent = self.model.get_consommation_by_source("NonExistentSource")
        self.assertEqual(len(conso_non_existent), 0)


    def test_get_consommation_entre_dates(self):
        # Assuming there is data for these dates from seed.sql
        date_debut = "2025-01-10 00:00:00"
        date_fin = "2025-01-11 00:00:00"
        
        conso_entre_dates = self.model.get_consommation_entre_dates(date_debut, date_fin)
        self.assertIsInstance(conso_entre_dates, list)
        self.assertGreater(len(conso_entre_dates), 0)
        for item in conso_entre_dates:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2) # (date_heure, energie_kwh)

        # Test with dates outside seeded data
        date_debut_future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        date_fin_future = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")
        conso_future = self.model.get_consommation_entre_dates(date_debut_future, date_fin_future)
        self.assertEqual(len(conso_future), 0)

    def test_get_consommation_by_equipement(self):
        # Use an equipement_id from seed data
        id_equipement = 1 
        conso_by_equipement = self.model.get_consommation_by_equipement(id_equipement)
        self.assertIsInstance(conso_by_equipement, list)
        self.assertGreater(len(conso_by_equipement), 0)
        for item in conso_by_equipement:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2) # (date_heure, energie_kwh)

        # Test a non-existent equipement
        conso_non_existent = self.model.get_consommation_by_equipement(99999)
        self.assertEqual(len(conso_non_existent), 0)

if __name__ == '__main__':
    unittest.main()
