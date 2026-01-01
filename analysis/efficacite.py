import numpy as np
from datetime import datetime, timedelta

from model.consommation_model import ConsommationModel
from model.equipement_model import EquipementModel
from model.type_equipement_model import TypeEquipementModel
from model.coupure_model import CoupureModel # Import CoupureModel

class Efficacite:
    def __init__(self):
        self.consommation_model = ConsommationModel()
        self.equipement_model = EquipementModel()
        self.type_equipement_model = TypeEquipementModel()
        self.coupure_model = CoupureModel() # Instantiate CoupureModel

    def calculer_efficacite_equipement(self, id_equipement):
        """
        Compare la consommation réelle d'un équipement à sa consommation théorique.
        
        Returns:
            dict: {
                "nom_equipement": str,
                "conso_reelle_totale": float (kWh),
                "conso_theorique_estimee": float (kWh),
                "ecart_kwh": float,
                "pourcentage_ecart": float (positive if real > theoretical)
            }
        """
        equip_details = self.equipement_model.get_equipement_details(id_equipement)
        if not equip_details:
            return None

        conso_theorique_type = equip_details["conso_theorique_type"] # kWh/heure pour le type
        
        # Obtenir toutes les consommations pour cet équipement
        all_conso_equip = self.consommation_model.get_consommation_by_equipement(id_equipement)
        if not all_conso_equip:
            return {
                "nom_equipement": equip_details["nom_equipement"],
                "conso_reelle_totale": 0.0,
                "conso_theorique_estimee": 0.0,
                "ecart_kwh": 0.0,
                "pourcentage_ecart": 0.0
            }

        conso_reelle_totale = sum(item[1] for item in all_conso_equip) # sum of energie_kwh

        # Estimer la consommation théorique basée sur la durée d'utilisation réelle
        # et la consommation théorique par heure du type d'équipement
        total_duree_minutes = sum(conso_item["duree_minutes"] for conso_item in self.consommation_model.get_all_consommation() if conso_item["id_equipement"] == id_equipement)
        total_heures_utilisation = total_duree_minutes / 60.0
        
        conso_theorique_estimee = conso_theorique_type * total_heures_utilisation # kWh

        ecart_kwh = conso_reelle_totale - conso_theorique_estimee
        pourcentage_ecart = (ecart_kwh / conso_theorique_estimee * 100) if conso_theorique_estimee else 0.0

        return {
            "nom_equipement": equip_details["nom_equipement"],
            "nom_batiment": equip_details["nom_batiment"], # Added nom_batiment
            "conso_reelle_totale": conso_reelle_totale,
            "conso_theorique_estimee": conso_theorique_estimee,
            "ecart_kwh": ecart_kwh,
            "pourcentage_ecart": pourcentage_ecart
        }

    def get_equipements_plus_energivores(self, top_n=5):
        """
        Identifie les équipements avec la consommation d'énergie totale la plus élevée.
        """
        all_consommations = self.consommation_model.get_all_consommation()
        
        # Agrégation par équipement
        conso_par_equipement = {}
        for conso in all_consommations:
            id_equipement = conso["id_equipement"]
            if id_equipement not in conso_par_equipement:
                conso_par_equipement[id_equipement] = 0.0
            conso_par_equipement[id_equipement] += conso["energie_kwh"]

        # Récupérer les détails des équipements et les trier
        equipements_energivores = []
        for id_equipement, total_kwh in conso_par_equipement.items():
            equip_details = self.equipement_model.get_equipement_details(id_equipement)
            if equip_details:
                equipements_energivores.append({
                    "nom_equipement": equip_details["nom_equipement"],
                    "total_kwh": total_kwh,
                    "nom_batiment": equip_details["nom_batiment"]
                })
        
        equipements_energivores.sort(key=lambda x: x["total_kwh"], reverse=True)
        return equipements_energivores[:top_n]

    def calculer_kwh_par_heure_utilisation(self, id_equipement):
        """
        Calcule la consommation moyenne en kWh par heure d'utilisation pour un équipement.
        """
        all_conso_equip = self.consommation_model.get_consommation_by_equipement(id_equipement)
        if not all_conso_equip:
            return 0.0

        total_energie_kwh = sum(item[1] for item in all_conso_equip)
        total_duree_minutes = sum(conso_item["duree_minutes"] for conso_item in self.consommation_model.get_all_consommation() if conso_item["id_equipement"] == id_equipement)
        
        if total_duree_minutes == 0:
            return 0.0
        
        total_heures_utilisation = total_duree_minutes / 60.0
        return total_energie_kwh / total_heures_utilisation if total_heures_utilisation else 0.0
    
    def calculer_rendement_par_type_equipement(self, id_type):
        """
        Calcule un "rendement" pour un type d'équipement en comparant la consommation
        moyenne réelle de tous les équipements de ce type à leur consommation théorique.
        
        Returns:
            dict: {
                "nom_type": str,
                "conso_theorique_type": float (kWh/heure),
                "conso_reelle_moyenne_par_heure": float (kWh/heure),
                "pourcentage_rendement": float (basé sur l'inverse de l'écart)
            }
        """
        type_details = self.type_equipement_model.get_type_equipement_details(id_type)
        if not type_details:
            return None

        conso_theorique_type = type_details["consommation_theorique"] # kWh/heure

        equipements_de_ce_type = [e for e in self.equipement_model.get_all_equipements() if e["id_type"] == id_type]
        if not equipements_de_ce_type:
            return {
                "nom_type": type_details["nom_type"],
                "conso_theorique_type": conso_theorique_type,
                "conso_reelle_moyenne_par_heure": 0.0,
                "pourcentage_rendement": 0.0
            }

        total_conso_reelle = 0.0
        total_heures_utilisation = 0.0

        for equip in equipements_de_ce_type:
            id_equipement = equip["id_equipement"]
            all_conso_equip = self.consommation_model.get_consommation_by_equipement(id_equipement)
            
            if all_conso_equip:
                total_conso_reelle += sum(item[1] for item in all_conso_equip)
                total_duree_minutes = sum(conso_item["duree_minutes"] for conso_item in self.consommation_model.get_all_consommation() if conso_item["id_equipement"] == id_equipement)
                total_heures_utilisation += total_duree_minutes / 60.0
        
        conso_reelle_moyenne_par_heure = total_conso_reelle / total_heures_utilisation if total_heures_utilisation else 0.0
        
        if conso_theorique_type == 0: # Avoid division by zero
            pourcentage_rendement = 0.0 # Or handle as error/undefined
        else:
            # If real is less than theoretical, efficiency > 100% (good)
            # If real is more than theoretical, efficiency < 100% (bad)
            # percentage_rendement = (conso_theorique_type / conso_reelle_moyenne_par_heure) * 100
            # A more intuitive "efficiency" might be how far real is from theoretical
            # (conso_theorique_type - conso_reelle_moyenne_par_heure) / conso_theorique_type * 100
            # Let's define it as how much "theoretical" is realized by "actual"
            pourcentage_rendement = (conso_reelle_moyenne_par_heure / conso_theorique_type) * 100 # >100% is less efficient

        return {
            "nom_type": type_details["nom_type"],
            "conso_theorique_type": conso_theorique_type,
            "conso_reelle_moyenne_par_heure": conso_reelle_moyenne_par_heure,
            "pourcentage_rendement": pourcentage_rendement
        }

    def detecter_gaspillage(self, seuil_ecart_pourcentage=20):
        """
        Détecte les équipements où la consommation réelle dépasse significativement
        la consommation théorique, indiquant un potentiel gaspillage.
        """
        equipements_en_gaspillage = []
        all_equipements = self.equipement_model.get_all_equipements()

        for equip in all_equipements:
            id_equipement = equip["id_equipement"]
            efficacite_data = self.calculer_efficacite_equipement(id_equipement)
            
            if efficacite_data and efficacite_data["pourcentage_ecart"] > seuil_ecart_pourcentage:
                equipements_en_gaspillage.append(efficacite_data)
        
        return equipements_en_gaspillage
    
    def analyze_conso_during_coupure(self):
        """
        Détecte la consommation d'énergie qui a eu lieu pendant une période de coupure.
        
        Returns:
            list: Une liste de dictionnaires, chaque dictionnaire représentant une instance
                  de consommation détectée pendant une coupure, avec les détails pertinents.
        """
        alerts = []
        all_coupures = self.coupure_model.get_all_coupures()
        all_consommations = self.consommation_model.get_all_consommation()

        for coupure in all_coupures:
            debut_coupure = datetime.fromisoformat(coupure["debut_coupure"])
            fin_coupure = datetime.fromisoformat(coupure["fin_coupure"]) if coupure["fin_coupure"] else datetime.now() # Assume ongoing coupures end now for analysis
            nom_batiment = coupure["nom_batiment"]

            for conso in all_consommations:
                conso_datetime = datetime.fromisoformat(conso["date_heure"])
                
                # Check if consumption occurred during the outage
                if debut_coupure <= conso_datetime <= fin_coupure:
                    alerts.append({
                        "type": "Consommation pdt Coupure",
                        "date": conso_datetime,
                        "description": f"Consommation de {conso['energie_kwh']:.2f} kWh sur {conso['nom_equipement']} ({nom_batiment}) "
                                       f"pendant une coupure (Début: {coupure['debut_coupure']}, Fin: {coupure['fin_coupure'] or 'En cours'})",
                        "equip_bat": f"{conso['nom_equipement']} ({nom_batiment})",
                        "energie_kwh": conso['energie_kwh'],
                        "id_conso": conso['id_conso'],
                        "id_equipement": conso['id_equipement']
                    })
        return alerts

