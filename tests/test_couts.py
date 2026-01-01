import unittest
from analysis.couts import Couts
from model.consommation_model import ConsommationModel
from model.source_model import SourceModel
import sqlite3
from config.settings import DB_PATH
from datetime import datetime

class TestCouts(unittest.TestCase):
    def setUp(self):
        self.couts_analyser = Couts()
        self.consommation_model = ConsommationModel()
        self.source_model = SourceModel()

        # Ensure known state for cout_kwh for testing
        # We assume the seed data has 'JIRAMA' and 'Groupe électrogène'
        self.jirama_cout_kwh = self.source_model.get_cout_kwh_by_source_name("JIRAMA")
        self.groupe_cout_kwh = self.source_model.get_cout_kwh_by_source_name("Groupe électrogène")
        
        # Manually calculated total energies from seed.sql for verification
        # JIRAMA: 1.1 + 0.6 + 3.2 + 1.0 + 0.5 + 3.1 + 1.2 + 0.6 + 3.3 = 14.6 kWh
        # Groupe électrogène: 1.4 + 0.8 + 3.9 + 7.5 = 13.6 kWh

    def test_calculer_cout_total_par_source(self):
        # Test JIRAMA
        total_cout_jirama = self.couts_analyser.calculer_cout_total_par_source("JIRAMA")
        expected_cout_jirama = 14.6 * self.jirama_cout_kwh # 14.6 * 0.20 = 2.92
        self.assertAlmostEqual(total_cout_jirama, expected_cout_jirama, places=2)

        # Test Groupe électrogène
        total_cout_groupe = self.couts_analyser.calculer_cout_total_par_source("Groupe électrogène")
        expected_cout_groupe = 13.6 * self.groupe_cout_kwh # 13.6 * 0.45 = 6.12
        self.assertAlmostEqual(total_cout_groupe, expected_cout_groupe, places=2)

        # Test non-existent source
        total_cout_non_existent = self.couts_analyser.calculer_cout_total_par_source("NonExistent")
        self.assertEqual(total_cout_non_existent, 0.0)

    def test_calculer_cout_total_jirama(self):
        total_cout_jirama = self.couts_analyser.calculer_cout_total_jirama()
        expected_cout_jirama = 14.6 * self.jirama_cout_kwh
        self.assertAlmostEqual(total_cout_jirama, expected_cout_jirama, places=2)

    def test_calculer_cout_total_groupe(self):
        total_cout_groupe = self.couts_analyser.calculer_cout_total_groupe()
        expected_cout_groupe = 13.6 * self.groupe_cout_kwh
        self.assertAlmostEqual(total_cout_groupe, expected_cout_groupe, places=2)

    def test_comparer_couts_sources(self):
        comparaison = self.couts_analyser.comparer_couts_sources()
        expected_jirama_cout = 14.6 * self.jirama_cout_kwh
        expected_groupe_cout = 13.6 * self.groupe_cout_kwh
        
        self.assertAlmostEqual(comparaison["JIRAMA"], expected_jirama_cout, places=2)
        self.assertAlmostEqual(comparaison["Groupe électrogène"], expected_groupe_cout, places=2)
        self.assertAlmostEqual(comparaison["difference"], expected_groupe_cout - expected_jirama_cout, places=2)

    def test_calculer_cout_par_periode(self):
        # Test par jour
        couts_jour = self.couts_analyser.calculer_cout_par_periode(periode='jour')
        
        # Expected values based on seed data and cout_kwh:
        # 2025-01-10: (1.1+0.6+3.2)*0.20 + (1.4+0.8+3.9+7.5)*0.45 = 4.9*0.20 + 13.6*0.45 = 0.98 + 6.12 = 7.10
        # 2025-01-11: (1.0+0.5+3.1)*0.20 = 4.6*0.20 = 0.92
        # 2025-01-12: (1.2+0.6+3.3)*0.20 = 5.1*0.20 = 1.02
        
        self.assertAlmostEqual(couts_jour["2025-01-10"], 7.10, places=2)
        self.assertAlmostEqual(couts_jour["2025-01-11"], 0.92, places=2)
        self.assertAlmostEqual(couts_jour["2025-01-12"], 1.02, places=2)

        # Test par mois
        couts_mois = self.couts_analyser.calculer_cout_par_periode(periode='mois')
        # Total: 7.10 + 0.92 + 1.02 = 9.04
        self.assertAlmostEqual(couts_mois["2025-01"], 9.04, places=2)
        
        # Test invalid period
        with self.assertRaises(ValueError):
            self.couts_analyser.calculer_cout_par_periode(periode='annee')

    def test_calculer_surcout_coupures(self):
        # This method is a placeholder and should return 0.0 for now.
        surcout = self.couts_analyser.calculer_surcout_coupures()
        self.assertEqual(surcout, 0.0)

if __name__ == '__main__':
    unittest.main()
