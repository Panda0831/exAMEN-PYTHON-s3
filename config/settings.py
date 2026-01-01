from pathlib import Path

# Racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Dossiers principaux
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Base de données
DB_PATH = DATA_DIR / "energie.db"
