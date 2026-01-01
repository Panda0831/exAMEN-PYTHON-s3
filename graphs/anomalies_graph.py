import matplotlib.pyplot as plt
from datetime import datetime
import sys
import os

# Ajout du chemin racine du projet pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from model.consommation_model import ConsommationModel
from analysis.statistiques import Statistique

def plot_anomalies(all_consommations, anomalies, output_path="graphs/anomalies.png"):
    """
    Génère un graphique de série temporelle de la consommation avec les anomalies mises en évidence.
    
    Args:
        all_consommations (list of dict): Liste de toutes les consommations.
        anomalies (list of dict): Liste des consommations identifiées comme des anomalies.
        output_path (str): Chemin pour sauvegarder l'image du graphique.
    """
    if not all_consommations:
        print("Aucune donnée de consommation à afficher pour le graphique d'anomalies.")
        return

    # Tri des données par date pour un tracé correct
    all_consommations.sort(key=lambda x: datetime.fromisoformat(x['date_heure']))
    
    dates = [datetime.fromisoformat(item['date_heure']) for item in all_consommations]
    energies = [item['energie_kwh'] for item in all_consommations]
    
    dates_anomalies = [datetime.fromisoformat(item['date_heure']) for item in anomalies]
    energies_anomalies = [item['energie_kwh'] for item in anomalies]

    plt.figure(figsize=(15, 8))
    plt.plot(dates, energies, label='Consommation Normale', color='blue', alpha=0.7, zorder=1)
    plt.scatter(dates_anomalies, energies_anomalies, color='red', s=100,
                label='Anomalies Détectées', zorder=2, edgecolors='black')

    plt.xlabel("Date et Heure")
    plt.ylabel("Consommation (kWh)")
    plt.title("Détection d'Anomalies de Consommation")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.gcf().autofmt_xdate() # Améliore le formatage des dates
    plt.tight_layout()

    plt.savefig(output_path)
    print(f"Graphique des anomalies sauvegardé dans : {output_path}")
    plt.close()

if __name__ == '__main__':
    print("Génération du graphique des anomalies (démonstration)...")
    
    consommation_model = ConsommationModel()
    statistique_analyzer = Statistique()
    
    all_data = consommation_model.get_all_consommation()
    anomalies_data = statistique_analyzer.anomalies(facteur=2)
    
    plot_anomalies(all_data, anomalies_data)
