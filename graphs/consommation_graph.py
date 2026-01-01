import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Ajout du chemin racine du projet pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Pour l'exemple, nous allons importer les classes nécessaires
from analysis.couts import Couts
from analysis.efficacite import Efficacite

def plot_consommation_par_jour(data_couts_par_jour, output_path="graphs/consommation_par_jour.png"):
    """
    Génère un graphique en barres de la consommation (coût) par jour.
    
    Args:
        data_couts_par_jour (dict): Dictionnaire avec les jours comme clés et les coûts comme valeurs.
        output_path (str): Chemin pour sauvegarder l'image du graphique.
    """
    if not data_couts_par_jour:
        print("Aucune donnée de consommation par jour à afficher.")
        return

    jours = list(data_couts_par_jour.keys())
    couts = list(data_couts_par_jour.values())

    plt.figure(figsize=(12, 7))
    plt.bar(jours, couts, color='skyblue')
    plt.xlabel("Jour")
    plt.ylabel("Coût Total (Ariary)")
    plt.title("Coût de la Consommation Énergétique par Jour")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    plt.savefig(output_path)
    print(f"Graphique de consommation par jour sauvegardé dans : {output_path}")
    plt.close()

def plot_consommation_par_equipement(data_energivores, output_path="graphs/consommation_par_equipement.png"):
    """
    Génère un diagramme circulaire (pie chart) montrant la répartition de la consommation
    parmi les équipements les plus énergivores.
    
    Args:
        data_energivores (list of dict): Liste des équipements les plus énergivores.
        output_path (str): Chemin pour sauvegarder l'image du graphique.
    """
    if not data_energivores:
        print("Aucune donnée sur les équipements énergivores à afficher.")
        return

    labels = [f"{item['nom_equipement']}\n({item['nom_batiment']})" for item in data_energivores]
    sizes = [item['total_kwh'] for item in data_energivores]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', startangle=90,
                                      pctdistance=0.85)

    # Cercle au centre pour faire un donut chart
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)

    ax.axis('equal')  # Assure que le pie chart est un cercle.
    plt.title("Répartition de la Consommation par Équipement (Top 5)", pad=20)
    ax.legend(wedges, labels,
              title="Équipements",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=10, weight="bold")
    plt.tight_layout()

    plt.savefig(output_path)
    print(f"Graphique de répartition par équipement sauvegardé dans : {output_path}")
    plt.close()

if __name__ == '__main__':
    print("Génération des graphiques de consommation (démonstration)...")
    
    # 1. Données pour le graphique par jour
    couts_analyzer = Couts()
    couts_par_jour_data = couts_analyzer.calculer_cout_par_periode(periode='jour')
    plot_consommation_par_jour(couts_par_jour_data)

    # 2. Données pour le graphique par équipement
    efficacite_analyzer = Efficacite()
    energivores_data = efficacite_analyzer.get_equipements_plus_energivores(top_n=5)
    plot_consommation_par_equipement(energivores_data)
