import unittest
import sqlite3
from datetime import datetime, timedelta

from model.coupure_model import CoupureModel
from config.settings import DB_PATH

class TestCoupureModel(unittest.TestCase):
    def setUp(self):
        self.model = CoupureModel()
        self.test_batiment_id = 2  # Assuming Hôpital Befelatanana exists from seed data
        
        # Ensure a clean state for testing
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        # Clean up any test data inserted
        self.cursor.execute("DELETE FROM COUPURE WHERE cause = 'Test Cause'")
        self.conn.commit()
        self.conn.close()

    def test_add_coupure(self):
        debut = datetime.now().replace(microsecond=0)
        fin = debut + timedelta(hours=1)
        
        coupure_id = self.model.add_coupure(self.test_batiment_id, debut.isoformat(), fin.isoformat(), "Test Cause")
        self.assertIsNotNone(coupure_id)
        self.assertIsInstance(coupure_id, int)

        # Verify insertion
        conn = self.model.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM COUPURE WHERE id_coupure = ?", (coupure_id,))
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result["id_batiment"], self.test_batiment_id)
        self.assertEqual(datetime.fromisoformat(result["debut_coupure"]), debut)
        self.assertEqual(datetime.fromisoformat(result["fin_coupure"]), fin)
        self.assertEqual(result["cause"], "Test Cause")

    def test_get_all_coupures(self):
        # Add a couple of test coupures
        debut1 = datetime(2025, 1, 1, 10, 0, 0)
        fin1 = datetime(2025, 1, 1, 11, 0, 0)
        self.model.add_coupure(self.test_batiment_id, debut1.isoformat(), fin1.isoformat(), "Test Cause")
        
        debut2 = datetime(2025, 1, 2, 14, 0, 0)
        self.model.add_coupure(self.test_batiment_id, debut2.isoformat(), None, "Test Cause") # ongoing
        
        all_coupures = self.model.get_all_coupures()
        self.assertIsInstance(all_coupures, list)
        self.assertGreaterEqual(len(all_coupures), 2) # At least the ones we just added

        # Check structure
        first_item = all_coupures[0]
        self.assertIn("id_coupure", first_item)
        self.assertIn("nom_batiment", first_item)
        self.assertIn("debut_coupure", first_item)

    def test_get_current_coupures(self):
        # Add an ongoing coupure
        debut = datetime.now().replace(microsecond=0) - timedelta(minutes=30)
        self.model.add_coupure(self.test_batiment_id, debut.isoformat(), None, "Test Cause")
        
        current_coupures = self.model.get_current_coupures()
        self.assertIsInstance(current_coupures, list)
        self.assertGreaterEqual(len(current_coupures), 1)
        
        # Verify that the added coupure is present and fin_coupure is None
        found = False
        for coupure in current_coupures:
            if coupure["id_batiment"] == self.test_batiment_id and coupure["cause"] == "Test Cause":
                self.assertIsNone(coupure["fin_coupure"])
                found = True
                break
        self.assertTrue(found, "Test current coupure not found")

    def test_get_coupures_by_period(self):
        # Add coupures within the period
        period_start = datetime(2025, 2, 1, 0, 0, 0)
        period_end = datetime(2025, 2, 28, 23, 59, 59)
        
        coupure_in_period = datetime(2025, 2, 15, 12, 0, 0)
        self.model.add_coupure(self.test_batiment_id, coupure_in_period.isoformat(), None, "Test Cause")
        
        # Add coupure outside the period
        coupure_outside_period = datetime(2025, 3, 1, 12, 0, 0)
        self.model.add_coupure(self.test_batiment_id, coupure_outside_period.isoformat(), None, "Another Cause")
        
        coupures_in_range = self.model.get_coupures_by_period(period_start.isoformat(), period_end.isoformat())
        self.assertIsInstance(coupures_in_range, list)
        self.assertGreaterEqual(len(coupures_in_range), 1) # At least the one we added
        
        # Verify the coupure is from the test_batiment_id and is the one added in period
        found = False
        for coupure in coupures_in_range:
            if coupure["id_batiment"] == self.test_batiment_id and coupure["cause"] == "Test Cause":
                found = True
                break
        self.assertTrue(found, "Coupure within period not found")
        
        # Verify the coupure outside the period is NOT found using a specific check on cause
        found_outside = False
        for coupure in coupures_in_range:
            if coupure["cause"] == "Another Cause":
                found_outside = True
                break
        self.assertFalse(found_outside, "Coupure outside period found unexpectedly")


if __name__ == '__main__':
    unittest.main()
