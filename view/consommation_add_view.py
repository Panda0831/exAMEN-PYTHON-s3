from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QMessageBox, QDateTimeEdit
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime # Moved this import to the top

from model.consommation_model import ConsommationModel
from model.equipement_model import EquipementModel
from model.source_model import SourceModel

class ConsommationAddView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une Consommation")
        self.setGeometry(300, 300, 500, 300)

        self.consommation_model = ConsommationModel()
        self.equipement_model = EquipementModel()
        self.source_model = SourceModel()

        self.main_layout = QVBoxLayout(self)

        self._create_input_fields()
        self._create_buttons()

    def _create_input_fields(self):
        # Equipement
        equipement_layout = QHBoxLayout()
        self.equipement_combo = QComboBox(self)
        self._load_equipements_to_combo()
        equipement_layout.addWidget(QLabel("Équipement:"))
        equipement_layout.addWidget(self.equipement_combo)
        self.main_layout.addLayout(equipement_layout)

        # Source
        source_layout = QHBoxLayout()
        self.source_combo = QComboBox(self)
        self._load_sources_to_combo()
        source_layout.addWidget(QLabel("Source:"))
        source_layout.addWidget(self.source_combo)
        self.main_layout.addLayout(source_layout)

        # Date et Heure
        datetime_layout = QHBoxLayout()
        self.datetime_input = QDateTimeEdit(self) # Replaced QLineEdit with QDateTimeEdit
        self.datetime_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss") # Set display format
        self.datetime_input.setDateTime(QDateTime.currentDateTime()) # Default to current time
        datetime_layout.addWidget(QLabel("Date/Heure:"))
        datetime_layout.addWidget(self.datetime_input)
        self.main_layout.addLayout(datetime_layout)

        # Durée
        duree_layout = QHBoxLayout()
        self.duree_input = QLineEdit(self)
        self.duree_input.setPlaceholderText("Durée (minutes)")
        duree_layout.addWidget(QLabel("Durée (min):"))
        duree_layout.addWidget(self.duree_input)
        self.main_layout.addLayout(duree_layout)

        # Énergie
        energie_layout = QHBoxLayout()
        self.energie_input = QLineEdit(self)
        self.energie_input.setPlaceholderText("Énergie (kWh)")
        energie_layout.addWidget(QLabel("Énergie (kWh):"))
        energie_layout.addWidget(self.energie_input)
        self.main_layout.addLayout(energie_layout)

    def _load_equipements_to_combo(self):
        equipements = self.equipement_model.get_all_equipements()
        self.equipement_combo.clear()
        for e in equipements:
            self.equipement_combo.addItem(f"{e['nom_equipement']} ({e['nom_batiment']})", e["id_equipement"])

    def _load_sources_to_combo(self):
        sources = self.source_model.get_all_sources()
        self.source_combo.clear()
        for s in sources:
            self.source_combo.addItem(s["nom_source"], s["id_source"])

    def _create_buttons(self):
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter", self)
        self.add_button.clicked.connect(self._add_consommation)
        button_layout.addWidget(self.add_button)

        self.cancel_button = QPushButton("Annuler", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(button_layout)

    def _add_consommation(self):
        id_equipement = self.equipement_combo.currentData()
        id_source = self.source_combo.currentData()
        datetime_str = self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss") # Read from QDateTimeEdit
        duree_str = self.duree_input.text()
        energie_str = self.energie_input.text()

        if not id_equipement or not id_source or not datetime_str or not duree_str or not energie_str:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return
        
        # Validate duree
        try:
            duree = int(duree_str)
            if duree <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erreur", "La durée doit être un entier positif.")
            return

        # Validate energie
        try:
            energie = float(energie_str)
            if energie < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erreur", "L'énergie doit être un nombre positif.")
            return
        
        # Add to model
        success, error_message = self.consommation_model.add_consommation(
            id_equipement, id_source, duree, energie, datetime_str
        )
        if success:
            QMessageBox.information(self, "Succès", "Consommation ajoutée avec succès.")
            self.accept() # Close dialog on success
        else:
            QMessageBox.warning(self, "Erreur d'Ajout", error_message)

if __name__ == '__main__':
    import sys
    import os
    # Adding project root to sys.path for model imports
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..')) # Go up one level from 'view'
    sys.path.insert(0, project_root) # Insert at the beginning of sys.path for priority

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    view = ConsommationAddView()
    view.exec()
    sys.exit(app.exec())
