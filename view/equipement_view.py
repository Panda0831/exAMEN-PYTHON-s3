from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QComboBox, QMessageBox
from PySide6.QtCore import Qt

from model.equipement_model import EquipementModel
from model.type_equipement_model import TypeEquipementModel
from model.batiment_model import BatimentModel # Assuming BatimentModel exists

class EquipementView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Équipements")
        self.setGeometry(200, 200, 800, 600)

        self.equipement_model = EquipementModel()
        self.type_equipement_model = TypeEquipementModel()
        self.batiment_model = BatimentModel() # Instantiate BatimentModel

        self.main_layout = QVBoxLayout(self)

        self._create_input_fields()
        self._create_table_widget()
        self._create_buttons()
        self._load_equipements()

    def _create_input_fields(self):
        input_layout = QHBoxLayout()

        self.nom_equipement_input = QLineEdit(self)
        self.nom_equipement_input.setPlaceholderText("Nom de l'équipement")
        input_layout.addWidget(QLabel("Nom:"))
        input_layout.addWidget(self.nom_equipement_input)

        self.puissance_watt_input = QLineEdit(self)
        self.puissance_watt_input.setPlaceholderText("Puissance (Watts)")
        input_layout.addWidget(QLabel("Puissance (W):"))
        input_layout.addWidget(self.puissance_watt_input)
        
        self.type_equipement_combo = QComboBox(self)
        self._load_type_equipements_to_combo()
        input_layout.addWidget(QLabel("Type:"))
        input_layout.addWidget(self.type_equipement_combo)

        self.batiment_combo = QComboBox(self)
        self._load_batiments_to_combo()
        input_layout.addWidget(QLabel("Bâtiment:"))
        input_layout.addWidget(self.batiment_combo)

        self.main_layout.addLayout(input_layout)

    def _load_type_equipements_to_combo(self):
        types = self.type_equipement_model.get_all_types_equipement()
        self.type_equipement_combo.clear()
        for t in types:
            self.type_equipement_combo.addItem(t["nom_type"], t["id_type"])

    def _load_batiments_to_combo(self):
        batiments = self.batiment_model.get_all_batiments() # Assuming BatimentModel has get_all_batiments
        self.batiment_combo.clear()
        for b in batiments:
            self.batiment_combo.addItem(b["nom"], b["id_batiment"])


    def _create_table_widget(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Nom", "Puissance (W)", "Type", "Bâtiment"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.table_widget.itemSelectionChanged.connect(self._selection_changed)
        self.main_layout.addWidget(self.table_widget)

    def _create_buttons(self):
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter", self)
        self.add_button.clicked.connect(self._add_equipement)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Modifier", self)
        self.edit_button.clicked.connect(self._edit_equipement)
        self.edit_button.setEnabled(False) # Disable until an item is selected
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Supprimer", self)
        self.delete_button.clicked.connect(self._delete_equipement)
        self.delete_button.setEnabled(False) # Disable until an item is selected
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

    def _load_equipements(self):
        self.table_widget.setRowCount(0)
        equipements = self.equipement_model.get_all_equipements()
        self.table_widget.setRowCount(len(equipements))
        for row, equip in enumerate(equipements):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(equip["id_equipement"])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(equip["nom_equipement"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(equip["puissance_watt"])))
            self.table_widget.setItem(row, 3, QTableWidgetItem(equip["nom_type"])) # Display nom_type
            self.table_widget.setItem(row, 4, QTableWidgetItem(equip["nom_batiment"])) # Display nom_batiment

    def _selection_changed(self):
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            # Populate input fields with selected data for editing
            row = selected_items[0].row()
            self.nom_equipement_input.setText(self.table_widget.item(row, 1).text())
            self.puissance_watt_input.setText(self.table_widget.item(row, 2).text())
            
            # Select correct item in QComboBox
            selected_type_name = self.table_widget.item(row, 3).text()
            index = self.type_equipement_combo.findText(selected_type_name)
            if index != -1:
                self.type_equipement_combo.setCurrentIndex(index)

            selected_batiment_name = self.table_widget.item(row, 4).text()
            index = self.batiment_combo.findText(selected_batiment_name)
            if index != -1:
                self.batiment_combo.setCurrentIndex(index)
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self._clear_input_fields()

    def _clear_input_fields(self):
        self.nom_equipement_input.clear()
        self.puissance_watt_input.clear()
        self.type_equipement_combo.setCurrentIndex(0)
        self.batiment_combo.setCurrentIndex(0)

    def _add_equipement(self):
        nom = self.nom_equipement_input.text()
        puissance_str = self.puissance_watt_input.text()
        id_type = self.type_equipement_combo.currentData()
        id_batiment = self.batiment_combo.currentData()

        if not nom or not puissance_str or id_type is None or id_batiment is None:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return

        try:
            puissance = float(puissance_str)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "La puissance doit être un nombre valide.")
            return
        
        # Add to model
        self.equipement_model.add_equipement(nom, puissance, id_type, id_batiment) # Assuming this method exists
        self._load_equipements()
        self._clear_input_fields()

    def _edit_equipement(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        id_equipement = int(self.table_widget.item(row, 0).text())
        nom = self.nom_equipement_input.text()
        puissance_str = self.puissance_watt_input.text()
        id_type = self.type_equipement_combo.currentData()
        id_batiment = self.batiment_combo.currentData()

        if not nom or not puissance_str or id_type is None or id_batiment is None:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return

        try:
            puissance = float(puissance_str)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "La puissance doit être un nombre valide.")
            return

        # Update model
        success, error_message = self.equipement_model.update_equipement(id_equipement, nom, puissance, id_type, id_batiment)
        if success:
            self._load_equipements()
            self._clear_input_fields()
        else:
            QMessageBox.warning(self, "Erreur de Modification", error_message)

    def _delete_equipement(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, "Confirmer Suppression",
                                     "Êtes-vous sûr de vouloir supprimer cet équipement ?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            id_equipement = int(self.table_widget.item(row, 0).text())
            self.equipement_model.delete_equipement(id_equipement) # Assuming this method exists
            self._load_equipements()
            self._clear_input_fields()


