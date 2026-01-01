# SmartEnergyMG

## 1. Introduction

SmartEnergyMG est une application de bureau conçue pour le suivi, l'analyse et la gestion de la consommation d'énergie. Développée en Python avec le framework Qt (PySide6), elle offre une interface graphique permettant de visualiser les données de consommation, d'analyser les coûts, de suivre les coupures de courant et d'évaluer l'efficacité énergétique des différents équipements et sources d'énergie.

Ce projet a été réalisé dans le cadre de l'examen de Python pour le niveau L2 SIO en janvier 2026.

## 2. Architecture du Projet

L'application est structurée selon une architecture de type **Modèle-Vue-Contrôleur (MVC)**, favorisant la séparation des préoccupations et la maintenabilité du code.

*   **Modèle (Model)**: Représente la couche de données de l'application. Il gère la logique métier, l'interaction avec la base de données (lecture, écriture) et la structure des données. Les fichiers se trouvent dans le répertoire `model/`.
*   **Vue (View)**: Constitue l'interface utilisateur (UI). Elle est responsable de l'affichage des données provenant du modèle et de la capture des interactions de l'utilisateur (clics, saisies). Les fichiers de la vue sont dans le répertoire `view/`.
*   **Contrôleur (Controller)**: Sert d'intermédiaire entre le Modèle et la Vue. Il reçoit les actions de l'utilisateur depuis la Vue, traite ces requêtes (en faisant appel au Modèle si nécessaire) et met à jour la Vue pour afficher les résultats. Les contrôleurs se trouvent dans le répertoire `controller/`.

```
Utilisateur -> interagit avec -> [ Vue ]
                                    |
                                    v
[ Contrôleur ] <- notifie les actions de l'utilisateur
     |
     v
[ Modèle ] <- met à jour les données
     |
     v
Base de Données
```

## 3. Structure des Répertoires

Voici une description détaillée de chaque répertoire et de son contenu :

| Répertoire             | Description                                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **`analysis/`**        | Contient les modules Python pour l'analyse des données (coûts, efficacité, statistiques).                                                |
| **`config/`**          | Fichiers de configuration : couleurs de l'UI, configuration de la base de données, et feuille de style QSS pour l'interface graphique.    |
| **`controller/`**      | Les contrôleurs qui lient les modèles aux vues. Chaque contrôleur gère la logique d'une fonctionnalité spécifique (consommation, etc.).  |
| **`data/`**            | Contient la base de données SQLite (`energie.db`) et le script SQL (`seed.sql`) pour l'initialiser avec des données de test.              |
| **`docs/`**            | Documentation du projet, y compris le sujet de l'examen.                                                                                 |
| **`graphs/`**          | Scripts pour générer des graphiques (via Matplotlib) et images des graphiques sauvegardés.                                                 |
| **`logs/`**            | Fichiers de log générés par l'application (non suivi par Git).                                                                           |
| **`model/`**           | Contient les modèles de données et la logique d'accès à la base de données. Chaque fichier `*_model.py` correspond à une table.           |
| **`tests/`**           | Tests unitaires pour assurer la fiabilité des différentes parties du code (modèles, analyses, etc.).                                     |
| **`utils/`**           | Fonctions et classes utilitaires transverses (manipulation de dates, logging, validation).                                               |
| **`view/`**            | Contient tous les composants de l'interface utilisateur (fenêtres principales, boîtes de dialogue, widgets personnalisés).                |
| **`view/components/`** | Widgets réutilisables qui composent les vues plus larges (tableaux, graphiques, cartes d'information).                                    |
| **`.venv/`**           | Environnement virtuel Python contenant les dépendances du projet.                                                                        |
| **`main.py`**          | **Point d'entrée de l'application.** Il initialise l'application Qt, charge le style et lance le contrôleur principal.                     |

## 4. Description des Fichiers Clés

### Fichiers Principaux
- `main.py`: Lance l'application.
- `README.md`: Ce fichier.

### `model/`
- `database.py`: Gère la connexion à la base de données SQLite.
- `consommation_model.py`: Gère les opérations CRUD pour la table `Consommation`.
- `equipement_model.py`: Gère les opérations CRUD pour la table `Equipement`.
- `coupure_model.py`: Gère les opérations CRUD pour la table `Coupure_Electricite`.
- `source_model.py`: Gère les opérations CRUD pour la table `Source_Energie`.
- ... (et ainsi de suite pour chaque table).

### `view/`
- `main_view.py`: La fenêtre principale de l'application.
- `dashboard_view.py`: Le tableau de bord principal affiché au lancement.
- `consommation_view.py`: Vue pour afficher les données de consommation.
- `components/matplotlib_widget.py`: Un widget personnalisé pour intégrer des graphiques Matplotlib dans l'interface Qt.

### `controller/`
- `main_controller.py`: Le contrôleur principal qui initialise la vue principale et gère la logique de haut niveau.
- `consommation_controller.py`: Gère les interactions de l'utilisateur dans la vue de consommation (par exemple, filtrer les données).

### `analysis/`
- `statistiques.py`: Fonctions pour calculer des statistiques sur la consommation.
- `couts.py`: Fonctions pour calculer les coûts énergétiques.
- `efficacite.py`: Fonctions pour analyser l'efficacité des sources d'énergie.

## 5. Schéma de la Base de Données

La base de données est stockée dans `data/energie.db` et sa structure est définie dans `data/seed.sql`.

- **`Batiment`**: Stocke les bâtiments.
  - `id_batiment` (INTEGER, PK), `nom` (TEXT)

- **`Type_Equipement`**: Définit les types d'équipements.
  - `id_type` (INTEGER, PK), `nom_type` (TEXT), `description` (TEXT)

- **`Equipement`**: Les équipements électriques, liés à un bâtiment et un type.
  - `id_equipement` (INTEGER, PK), `nom` (TEXT), `id_batiment` (FK), `id_type` (FK), `puissance_W` (REAL)

- **`Source_Energie`**: Les sources d'énergie disponibles.
  - `id_source` (INTEGER, PK), `nom_source` (TEXT), `cout_kWh` (REAL)

- **`Consommation`**: Enregistrements de la consommation d'énergie.
  - `id_consommation` (INTEGER, PK), `id_equipement` (FK), `id_source` (FK), `date_debut` (TEXT), `date_fin` (TEXT), `energie_kWh` (REAL)

- **`Coupure_Electricite`**: Journal des coupures de courant.
  - `id_coupure` (INTEGER, PK), `date_debut` (TEXT), `date_fin` (TEXT)

## 6. Comment Lancer le Projet

### Prérequis
- Python 3.10 ou supérieur.
- Les dépendances listées dans `requirements.txt` (si ce fichier existe) ou installables manuellement.

### Installation
1.  **Clonez le projet :**
    ```bash
    git clone <URL_DU_PROJET>
    cd SmartEnergyMG
    ```

2.  **Créez un environnement virtuel :**
    ```bash
    python -m venv .venv
    ```

3.  **Activez l'environnement :**
    - Sur Windows : `.venv\Scripts\activate`
    - Sur macOS/Linux : `source .venv/bin/activate`

4.  **Installez les dépendances :**
    *Note: Un fichier `requirements.txt` serait idéal. En son absence, les dépendances principales sont à installer manuellement.*
    ```bash
    pip install PySide6 numpy pandas matplotlib
    ```

### Exécution

Pour lancer l'application, exécutez le script `main.py` à la racine du projet :

```bash
python main.py
```

## 7. Lancer les Tests

Pour exécuter les tests unitaires et s'assurer que tout fonctionne comme prévu :

```bash
python -m unittest discover tests
```
