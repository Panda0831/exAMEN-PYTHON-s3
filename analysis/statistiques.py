import numpy as np
from datetime import datetime, timedelta # Added timedelta
from model.consommation_model import ConsommationModel

class Statistique :
    def __init__(self):
        self.model = ConsommationModel()
    
    def stat_globale(self):
        data = self.model.get_all_consommation()
        valeur = np.array([row["energie_kwh"]for row in data])
        if len(valeur) == 0:
            return None
        return {
            "total_kwh": np.sum(valeur),
            "moyenne_kwh": np.mean(valeur),
            "max_kwh": np.max(valeur),
            "min_kwh": np.min(valeur),
            "ecart_type": np.std(valeur)
        }
    def anomalies(self, facteur=2):
        data = self.model.get_all_consommation()
        if not data:
            return []
            
        valeur = np.array([row["energie_kwh"] for row in data])
        
        moyenne = np.mean(valeur)
        ecart_type = np.std(valeur)

        if ecart_type == 0:
            return []

        seuil = moyenne + facteur * ecart_type
        
        anomalies = [row for row in data if row["energie_kwh"] > seuil]
        return anomalies
    
    def consommation_par_source(self, nom_source):
        data = self.model.get_consommation_by_source(nom_source)
        if not data:
            return 0
        valeur = np.array([r["energie_kwh"] for r in data])
        return np.sum(valeur)
        
    def agreger_par_periode(self, consommations, periode='jour'):
        """
        Agrège les données de consommation par période (jour, mois).

        Args:
            consommations (list of tuples): Liste de tuples (datetime_obj, energie_kwh).
            periode (str): 'jour' ou 'mois'.

        Returns:
            dict: Un dictionnaire avec les dates (tronquées) comme clés et la somme
                  des énergies comme valeurs.
        """
        if not consommations:
            return {}
            
        agregees = {}
        for datetime_obj, energie in consommations:
            cle = None
            if periode == 'jour':
                cle = datetime_obj.date()
            elif periode == 'semaine': # Week aggregation (Monday as start of week)
                start_of_week = datetime_obj.date() - timedelta(days=datetime_obj.weekday())
                cle = start_of_week
            elif periode == 'mois':
                cle = datetime_obj.strftime('%Y-%m')
            else:
                raise ValueError("La période doit être 'jour', 'semaine' ou 'mois'.")
                
            cle_str = str(cle)
            if cle_str not in agregees:
                agregees[cle_str] = 0
            agregees[cle_str] += energie
            
        return agregees

    