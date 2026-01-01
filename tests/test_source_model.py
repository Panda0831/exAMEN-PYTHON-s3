import unittest
import sqlite3
from model.source_model import SourceModel
from config.settings import DB_PATH

class TestSourceModel(unittest.TestCase):
    def setUp(self):
        self.model = SourceModel()
        self.test_source_name = "TestSource"
        # Ensure a clean state for testing
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        # Clean up any test data inserted
        self.cursor.execute("DELETE FROM SOURCE_ENERGIE WHERE nom_source = ?", (self.test_source_name,))
        self.conn.commit()
        self.conn.close()

    def test_add_source(self):
        # Test adding a new source
        source_id = self.model.add_source(self.test_source_name, 0.50, "Description de test")
        self.assertIsNotNone(source_id)
        self.assertIsInstance(source_id, int)

        # Verify the source was added
        conn = self.model.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT nom_source, cout_kwh, description FROM SOURCE_ENERGIE WHERE id_source = ?", (source_id,))
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result["nom_source"], self.test_source_name)
        self.assertEqual(result["cout_kwh"], 0.50)
        self.assertEqual(result["description"], "Description de test")

    def test_add_existing_source(self):
        # Add the source first
        self.model.add_source(self.test_source_name, 0.50)
        
        # Try to add it again - should return None due to IntegrityError
        source_id = self.model.add_source(self.test_source_name, 0.60)
        self.assertIsNone(source_id)
        
        # Ensure it didn't update the existing one
        conn = self.model.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT cout_kwh FROM SOURCE_ENERGIE WHERE nom_source = ?", (self.test_source_name,))
        result = cursor.fetchone()
        conn.close()
        self.assertEqual(result["cout_kwh"], 0.50)
        
    def test_get_cout_kwh_by_source_name(self):
        # Add a source for testing
        self.model.add_source(self.test_source_name, 0.75, "Another test")
        
        # Test fetching cost
        cout = self.model.get_cout_kwh_by_source_name(self.test_source_name)
        self.assertEqual(cout, 0.75)
        
        # Test non-existent source
        cout_non_existent = self.model.get_cout_kwh_by_source_name("NonExistent")
        self.assertIsNone(cout_non_existent)

    def test_get_source_id_by_name(self):
        source_id = self.model.add_source(self.test_source_name, 0.75, "Another test")
        
        # Test fetching ID
        fetched_id = self.model.get_source_id_by_name(self.test_source_name)
        self.assertEqual(fetched_id, source_id)
        
        # Test non-existent source
        id_non_existent = self.model.get_source_id_by_name("NonExistent")
        self.assertIsNone(id_non_existent)
        
    def test_get_all_sources(self):
        # Ensure at least one source is in the DB (from seed or this test)
        all_sources = self.model.get_all_sources()
        self.assertIsInstance(all_sources, list)
        self.assertGreater(len(all_sources), 0)
        
        # Check structure of one item
        first_item = all_sources[0]
        self.assertIn("id_source", first_item)
        self.assertIn("nom_source", first_item)
        self.assertIn("cout_kwh", first_item)


if __name__ == '__main__':
    unittest.main()
