from model.consommation_model import ConsommationModel
from model.source_model import SourceModel
from datetime import datetime


class Couts:
    def __init__(self):
        self.consommation_model = ConsommationModel()
        self.source_model = SourceModel()

    # ---------------------------
    # Récupération coût kWh
    # ---------------------------
    def _get_cout_kwh(self, nom_source):
        return self.source_model.get_cout_kwh_by_source_name(nom_source)

    # ---------------------------
    # Coût total par source
    # ---------------------------
    def calculer_cout_total_par_source(self, nom_source):
        cout_kwh = self._get_cout_kwh(nom_source)
        if cout_kwh is None:
            return 0.0

        consommations = self.consommation_model.get_consommation_by_source(nom_source)
        total_energie_kwh = sum(item["energie_kwh"] for item in consommations)

        return total_energie_kwh * cout_kwh

    def calculer_cout_total_jirama(self):
        return self.calculer_cout_total_par_source("JIRAMA")

    def calculer_cout_total_groupe(self):
        return self.calculer_cout_total_par_source("Groupe électrogène")

    # ---------------------------
    # Comparaison
    # ---------------------------
    def comparer_couts_sources(self):
        cout_jirama = self.calculer_cout_total_jirama()
        cout_groupe = self.calculer_cout_total_groupe()

        return {
            "JIRAMA": cout_jirama,
            "Groupe électrogène": cout_groupe,
            "difference": cout_groupe - cout_jirama
        }

    # ---------------------------
    # Coût par période
    # ---------------------------
    def calculer_cout_par_periode(self, periode="jour"):
        all_consommations = self.consommation_model.get_all_consommation()
        couts_agreges = {}

        for conso in all_consommations:
            date_heure = datetime.fromisoformat(conso["date_heure"])
            energie_kwh = conso["energie_kwh"]
            nom_source = conso["nom_source"]

            cout_kwh = self._get_cout_kwh(nom_source)
            if cout_kwh is None:
                continue

            if periode == "jour":
                cle = date_heure.date().isoformat()
            elif periode == "mois":
                cle = date_heure.strftime("%Y-%m")
            else:
                raise ValueError("La période doit être 'jour' ou 'mois'.")

            couts_agreges.setdefault(cle, 0.0)
            couts_agreges[cle] += energie_kwh * cout_kwh

        return couts_agreges

    # ---------------------------
    # Surcoût des coupures (placeholder)
    # ---------------------------
    def calculer_surcout_coupures(self):
        # À implémenter avec CoupureModel
        return 0.0

    def simuler_impact_coupure(self, start_datetime, duration_hours):
        """
        Simule l'impact financier d'une coupure JIRAMA en estimant le coût
        supplémentaire si un groupe électrogène est utilisé.
        
        Args:
            start_datetime (datetime): La date et l'heure de début de la coupure simulée.
            duration_hours (float): La durée estimée de la coupure en heures.
            
        Returns:
            tuple: (estimated_cost, error_message)
                   estimated_cost (float or None): Le coût supplémentaire estimé.
                   error_message (str or None): Message d'erreur si la simulation échoue.
        """
        if duration_hours <= 0:
            return None, "La durée de la simulation doit être un nombre positif."

        # 1. Get generator cost per kWh
        generator_cout_kwh = self.source_model.get_cout_kwh_by_source_name("Groupe électrogène")
        if generator_cout_kwh is None:
            return None, "Coût du 'Groupe électrogène' non trouvé. Assurez-vous qu'il est configuré."

        # 2. Estimate average consumption per hour
        all_consos = self.consommation_model.get_all_consommation()
        if not all_consos:
            return None, "Aucune donnée de consommation disponible pour estimer l'impact."
        
        total_kwh = sum(c["energie_kwh"] for c in all_consos)
        
        # Calculate total duration in hours for all recorded consumptions
        # This is a simplification; a more accurate model would consider only "active" hours or specific periods.
        total_duree_minutes = sum(c["duree_minutes"] for c in all_consos)
        total_duree_hours = total_duree_minutes / 60.0
        
        if total_duree_hours == 0:
            return None, "Durée totale de consommation enregistrée est nulle, impossible d'estimer la moyenne."

        average_kwh_per_hour = total_kwh / total_duree_hours

        # 3. Calculate estimated kWh during the simulated outage
        estimated_kwh_during_outage = average_kwh_per_hour * duration_hours

        # 4. Calculate estimated additional cost
        estimated_cost = estimated_kwh_during_outage * generator_cout_kwh
        
        return estimated_cost, None

