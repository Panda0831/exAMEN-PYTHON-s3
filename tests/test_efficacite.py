import unittest
from analysis.efficacite import Efficacite
from model.consommation_model import ConsommationModel
from model.equipement_model import EquipementModel
from model.type_equipement_model import TypeEquipementModel
import numpy as np

class TestEfficacite(unittest.TestCase):
    def setUp(self):
        self.efficacite_analyser = Efficacite()
        self.consommation_model = ConsommationModel()
        self.equipement_model = EquipementModel()
        self.type_equipement_model = TypeEquipementModel()

        # Assuming seed data is loaded and available
        # Equipements:
        # 1: Salle Info 1 (Type: Informatique, conso_theorique_type: 1.2 kWh/heure)
        # 2: Amphi A (Type: Éclairage, conso_theorique_type: 0.5 kWh/heure)
        # 3: Clim Centrale (Type: Climatisation, conso_theorique_type: 3.0 kWh/heure)
        # 4: Bloc opératoire (Type: Laboratoire, conso_theorique_type: 2.5 kWh/heure)
        # 5: Salle Urgences (Type: Éclairage, conso_theorique_type: 0.5 kWh/heure)

        # Consommations for id_equipement=1 (Salle Info 1)
        # (1, 1, '2025-01-10 07:00:00', 60, 1.1)
        # (1, 2, '2025-01-10 09:00:00', 60, 1.4)
        # (1, 1, '2025-01-11 08:00:00', 60, 1.0)
        # (1, 1, '2025-01-12 08:00:00', 60, 1.2)
        # Total conso réelle: 1.1 + 1.4 + 1.0 + 1.2 = 4.7 kWh
        # Total durée: 4 * 60 minutes = 240 minutes = 4 heures
        # Conso théorique estimée: 1.2 kWh/heure * 4 heures = 4.8 kWh

    def test_calculer_efficacite_equipement(self):
        # Test for id_equipement=1 (Salle Info 1)
        efficacite = self.efficacite_analyser.calculer_efficacite_equipement(1)
        self.assertIsNotNone(efficacite)
        self.assertEqual(efficacite["nom_equipement"], "Salle Info 1")
        self.assertAlmostEqual(efficacite["conso_reelle_totale"], 4.7, places=2)
        self.assertAlmostEqual(efficacite["conso_theorique_estimee"], 4.8, places=2)
        self.assertAlmostEqual(efficacite["ecart_kwh"], -0.1, places=2)
        self.assertAlmostEqual(efficacite["pourcentage_ecart"], -2.08, places=2) # (-0.1 / 4.8) * 100

        # Test for non-existent equipment
        efficacite_non_existent = self.efficacite_analyser.calculer_efficacite_equipement(999)
        self.assertIsNone(efficacite_non_existent)

    def test_get_equipements_plus_energivores(self):
        energivores = self.efficacite_analyser.get_equipements_plus_energivores(top_n=2)
        self.assertEqual(len(energivores), 2)
        # Expected from seed data (total kWh):
        # Equipement 3 (Clim Centrale): 3.2 + 3.9 + 7.5 + 3.1 + 3.3 = 21.0 kWh
        # Equipement 1 (Salle Info 1): 1.1 + 1.4 + 1.0 + 1.2 = 4.7 kWh
        # Equipement 2 (Amphi A): 0.6 + 0.8 + 0.5 + 0.6 = 2.5 kWh
        # Equipement 4 (Bloc opératoire): 0.0 (no consumption data in seed for this, just an equipment)
        # Equipement 5 (Salle Urgences): 0.0 (no consumption data in seed for this)
        
        self.assertEqual(energivores[0]["nom_equipement"], "Clim Centrale")
        self.assertAlmostEqual(energivores[0]["total_kwh"], 21.0, places=2)
        self.assertEqual(energivores[1]["nom_equipement"], "Salle Info 1")
        self.assertAlmostEqual(energivores[1]["total_kwh"], 4.7, places=2)

    def test_calculer_kwh_par_heure_utilisation(self):
        # Test for id_equipement=1 (Salle Info 1)
        # Total conso réelle: 4.7 kWh
        # Total durée: 4 heures
        kwh_par_heure = self.efficacite_analyser.calculer_kwh_par_heure_utilisation(1)
        self.assertAlmostEqual(kwh_par_heure, 4.7 / 4.0, places=2) # 1.175

        # Test for equipment with no consumption data (e.g., Equipement 4)
        kwh_par_heure_zero = self.efficacite_analyser.calculer_kwh_par_heure_utilisation(4)
        self.assertEqual(kwh_par_heure_zero, 0.0)

    def test_calculer_rendement_par_type_equipement(self):
        # Test for id_type=3 (Informatique) -> Equipement 1 (Salle Info 1)
        # conso_theorique_type: 1.2 kWh/heure
        # conso_reelle_moyenne_par_heure for Salle Info 1: 4.7 kWh / 4 heures = 1.175 kWh/heure
        # rendement: (1.175 / 1.2) * 100 = 97.916...
        rendement_informatique = self.efficacite_analyser.calculer_rendement_par_type_equipement(3)
        self.assertIsNotNone(rendement_informatique)
        self.assertEqual(rendement_informatique["nom_type"], "Informatique")
        self.assertAlmostEqual(rendement_informatique["conso_theorique_type"], 1.2, places=2)
        self.assertAlmostEqual(rendement_informatique["conso_reelle_moyenne_par_heure"], 1.175, places=3)
        self.assertAlmostEqual(rendement_informatique["pourcentage_rendement"], 97.917, places=3)

        # Test for a type with no associated equipment
        rendement_non_existent = self.efficacite_analyser.calculer_rendement_par_type_equipement(999)
        self.assertIsNone(rendement_non_existent)
        
        # Test for a type with equipment but no consumption
        # Type 4: Laboratoire (Equipement 4: Bloc opératoire)
        # Conso théorique type: 2.5 kWh/heure
        # Conso réelle moyenne par heure: 0.0
        rendement_laboratoire = self.efficacite_analyser.calculer_rendement_par_type_equipement(4)
        self.assertIsNotNone(rendement_laboratoire)
        self.assertEqual(rendement_laboratoire["nom_type"], "Laboratoire")
        self.assertAlmostEqual(rendement_laboratoire["conso_theorique_type"], 2.5, places=2)
        self.assertAlmostEqual(rendement_laboratoire["conso_reelle_moyenne_par_heure"], 0.0, places=2)
        self.assertAlmostEqual(rendement_laboratoire["pourcentage_rendement"], 0.0, places=2)


    def test_detecter_gaspillage(self):
        # Let's consider Clim Centrale (id_equipement=3)
        # conso_theorique_type: 3.0 kWh/heure
        # Conso réelle totale: 21.0 kWh
        # Total durée: 5 * 60 minutes = 300 minutes = 5 heures
        # Conso théorique estimée: 3.0 kWh/heure * 5 heures = 15.0 kWh
        # Ecart: 21.0 - 15.0 = 6.0 kWh
        # Pourcentage écart: (6.0 / 15.0) * 100 = 40%

        # Both should be detected with a threshold of 20%
        gaspillage = self.efficacite_analyser.detecter_gaspillage(seuil_ecart_pourcentage=20)
        self.assertEqual(len(gaspillage), 2)
        
        # Check that both expected equipments are in the list
        noms_gaspillage = [item["nom_equipement"] for item in gaspillage]
        self.assertIn("Clim Centrale", noms_gaspillage)
        self.assertIn("Amphi A", noms_gaspillage)

        # Check Clim Centrale's percentage
        clim_centrale_gaspillage = next(item for item in gaspillage if item["nom_equipement"] == "Clim Centrale")
        self.assertAlmostEqual(clim_centrale_gaspillage["pourcentage_ecart"], 40.0, places=2)

        # Check Amphi A's percentage
        amphi_a_gaspillage = next(item for item in gaspillage if item["nom_equipement"] == "Amphi A")
        self.assertAlmostEqual(amphi_a_gaspillage["pourcentage_ecart"], 25.0, places=2)

        # Test with higher threshold (50%) - should detect nothing
        gaspillage_high_seuil = self.efficacite_analyser.detecter_gaspillage(seuil_ecart_pourcentage=50)
        self.assertEqual(len(gaspillage_high_seuil), 0)

if __name__ == '__main__':
    unittest.main()
