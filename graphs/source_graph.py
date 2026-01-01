import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Ajout du chemin racine du projet pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis.couts import Couts

def plot_comparaison_sources(data_comparaison, output_path="graphs/comparaison_sources.png"):
    """
    Génère un graphique en barres comparant les coûts totaux des sources d'énergie.
    
    Args:
        data_comparaison (dict): Dictionnaire avec les noms des sources et leurs coûts.
                                 Ex: {"JIRAMA": 1000, "Groupe électrogène": 3000, "difference": 2000}
        output_path (str): Chemin pour sauvegarder l'image du graphique.
    """
    sources = [key for key in data_comparaison.keys() if key != "difference"]
    couts = [data_comparaison[key] for key in sources]

    if not sources:
        print("Aucune donnée de comparaison de sources à afficher.")
        return
    
    colors = ['#4A90E2', '#D0021B'] # Bleu pour JIRAMA, Rouge pour Groupe

    plt.figure(figsize=(8, 6))
    bars = plt.bar(sources, couts, color=colors)
    plt.xlabel("Source d'Énergie")
    plt.ylabel("Coût Total (Ariary)")
    plt.title("Comparaison des Coûts Totaux par Source d'Énergie")
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Ajouter les valeurs sur les barres
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:,.2f} Ar', va='bottom', ha='center')

    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Graphique de comparaison des sources sauvegardé dans : {output_path}")
    plt.close()

if __name__ == '__main__':
    print("Génération du graphique de comparaison des sources (démonstration)...")
    
    couts_analyzer = Couts()
    data_comparaison_sources = couts_analyzer.comparer_couts_sources()
    plot_comparaison_sources(data_comparaison_sources)
