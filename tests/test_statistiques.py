import unittest
import numpy as np

from analysis.statistiques import Statistique
from model.consommation_model import ConsommationModel

class TestStatistique(unittest.TestCase):
    def setUp(self):
        self.statistique = Statistique()
        self.consommation_model = ConsommationModel()
        
        # We rely on the seeded data for these tests.
        # Make sure seed data is present before running tests.

    def test_stat_globale(self):
        stats = self.statistique.stat_globale()
        
        # Get data directly from model to verify
        data = self.consommation_model.get_all_consommation()
        energies = np.array([row["energie_kwh"] for row in data])

        self.assertIsNotNone(stats)
        self.assertAlmostEqual(stats['total_kwh'], np.sum(energies))
        self.assertAlmostEqual(stats['moyenne_kwh'], np.mean(energies))
        self.assertEqual(stats['max_kwh'], np.max(energies))
        self.assertEqual(stats['min_kwh'], np.min(energies))
        self.assertAlmostEqual(stats['ecart_type'], np.std(energies))

    def test_anomalies(self):
        # The seeded data has one value (7.5) that is a bit higher than others.
        # Let's see if we can catch it.
        # Data: 1.1, 0.6, 3.2, 1.4, 0.8, 3.9, 7.5, 1.0, 0.5, 3.1, 1.2, 0.6, 3.3
        # Mean is approx 2.55, std is approx 2.0.
        # Z-score for 7.5 is (7.5 - 2.55) / 2.0 = 2.475
        
        # Using a factor of 2 should catch the 7.5 kWh consumption
        anomalies = self.statistique.anomalies(facteur=2)
        self.assertIsInstance(anomalies, list)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]['energie_kwh'], 7.5)

        # Using a higher factor should not find any anomalies
        anomalies_high_factor = self.statistique.anomalies(facteur=3)
        self.assertEqual(len(anomalies_high_factor), 0)

    def test_consommation_par_source(self):
        # Test with 'JIRAMA'
        total_jirama = self.statistique.consommation_par_source('JIRAMA')
        
        # Manually calculate from seed data
        # 1.1 + 0.6 + 3.2 + 1.0 + 0.5 + 3.1 + 1.2 + 0.6 + 3.3 = 14.6
        self.assertAlmostEqual(total_jirama, 14.6)
        
        # Test with 'Groupe électrogène'
        total_groupe = self.statistique.consommation_par_source('Groupe électrogène')
        # Manually calculate from seed data
        # 1.4 + 0.8 + 3.9 + 7.5 = 13.6
        self.assertAlmostEqual(total_groupe, 13.6)
        
        # Test non-existent source
        total_non_existent = self.statistique.consommation_par_source('NonExistent')
        self.assertEqual(total_non_existent, 0)

if __name__ == '__main__':
    unittest.main()