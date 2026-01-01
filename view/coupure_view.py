from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QComboBox, QMessageBox, QTextEdit, QDateTimeEdit
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime

from model.coupure_model import CoupureModel
from model.batiment_model import BatimentModel

class CoupureView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Coupures")
        self.setGeometry(250, 250, 850, 650)

        self.coupure_model = CoupureModel()
        self.batiment_model = BatimentModel()

        self.main_layout = QVBoxLayout(self)

        self._create_input_fields()
        self._create_table_widget()
        self._create_buttons()
        self._load_coupures()

    def _create_input_fields(self):
        input_layout_top = QHBoxLayout()

        self.batiment_combo = QComboBox(self)
        self._load_batiments_to_combo()
        input_layout_top.addWidget(QLabel("Bâtiment:"))
        input_layout_top.addWidget(self.batiment_combo)

        self.debut_coupure_input = QDateTimeEdit(self)
        self.debut_coupure_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.debut_coupure_input.setDateTime(QDateTime.currentDateTime()) # Default to current time
        input_layout_top.addWidget(QLabel("Début:"))
        input_layout_top.addWidget(self.debut_coupure_input)

        self.fin_coupure_input = QDateTimeEdit(self)
        self.fin_coupure_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.fin_coupure_input.setCalendarPopup(True) # Allow calendar popup
        # self.fin_coupure_input.setMinimumDateTime(self.debut_coupure_input.dateTime()) # Optional: enforce order
        input_layout_top.addWidget(QLabel("Fin:"))
        input_layout_top.addWidget(self.fin_coupure_input)
        
        self.main_layout.addLayout(input_layout_top)

        input_layout_bottom = QHBoxLayout()
        self.cause_input = QTextEdit(self) # Use QTextEdit for potentially longer cause descriptions
        self.cause_input.setPlaceholderText("Cause de la coupure (optionnel)")
        self.cause_input.setMaximumHeight(60) # Limit height for text edit
        input_layout_bottom.addWidget(QLabel("Cause:"))
        input_layout_bottom.addWidget(self.cause_input)
        self.main_layout.addLayout(input_layout_bottom)


    def _load_batiments_to_combo(self):
        batiments = self.batiment_model.get_all_batiments()
        self.batiment_combo.clear()
        for b in batiments:
            self.batiment_combo.addItem(b["nom"], b["id_batiment"])


    def _create_table_widget(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Bâtiment", "Début", "Fin", "Cause"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.table_widget.itemSelectionChanged.connect(self._selection_changed)
        self.main_layout.addWidget(self.table_widget)

    def _create_buttons(self):
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter", self)
        self.add_button.clicked.connect(self._add_coupure)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Modifier", self)
        self.edit_button.clicked.connect(self._edit_coupure)
        self.edit_button.setEnabled(False) # Disable until an item is selected
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Supprimer", self)
        self.delete_button.clicked.connect(self._delete_coupure)
        self.delete_button.setEnabled(False) # Disable until an item is selected
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

    def _load_coupures(self):
        self.table_widget.setRowCount(0)
        coupures = self.coupure_model.get_all_coupures()
        self.table_widget.setRowCount(len(coupures))
        for row, cp in enumerate(coupures):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(cp["id_coupure"])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(cp["nom_batiment"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(cp["debut_coupure"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(cp["fin_coupure"] or "En cours"))
            self.table_widget.setItem(row, 4, QTableWidgetItem(cp["cause"] or "N/A"))

    def _selection_changed(self):
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            row = selected_items[0].row()
            
            # Populate input fields
            selected_batiment_name = self.table_widget.item(row, 1).text()
            index = self.batiment_combo.findText(selected_batiment_name)
            if index != -1:
                self.batiment_combo.setCurrentIndex(index)
            
            self.debut_coupure_input.setDateTime(QDateTime.fromString(self.table_widget.item(row, 2).text(), "yyyy-MM-dd HH:mm:ss"))
            
            fin_text = self.table_widget.item(row, 3).text()
            if fin_text == "En cours":
                self.fin_coupure_input.setDateTime(QDateTime()) # Set to null/invalid QDateTime
            else:
                self.fin_coupure_input.setDateTime(QDateTime.fromString(fin_text, "yyyy-MM-dd HH:mm:ss"))
            
            cause_text = self.table_widget.item(row, 4).text()
            self.cause_input.setText("" if cause_text == "N/A" else cause_text)
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self._clear_input_fields()

    def _clear_input_fields(self):
        self.batiment_combo.setCurrentIndex(0)
        self.debut_coupure_input.setDateTime(QDateTime.currentDateTime())
        self.fin_coupure_input.setDateTime(QDateTime()) # Clear or set to null datetime
        self.cause_input.clear()


    def _add_coupure(self):
        id_batiment = self.batiment_combo.currentData()
        debut_str = self.debut_coupure_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        fin_datetime = self.fin_coupure_input.dateTime()
        fin_str = fin_datetime.toString("yyyy-MM-dd HH:mm:ss") if fin_datetime.isValid() else None
        cause = self.cause_input.toPlainText() or None

        if not debut_str or id_batiment is None:
            QMessageBox.warning(self, "Erreur", "Le bâtiment et la date de début sont obligatoires.")
            return
        
        # Convert to datetime objects for comparison
        debut_dt = datetime.fromisoformat(debut_str)
        fin_dt = datetime.fromisoformat(fin_str) if fin_str else None

        if fin_dt and fin_dt <= debut_dt:
            QMessageBox.warning(self, "Erreur", "La date de fin doit être postérieure à la date de début.")
            return

        result = self.coupure_model.add_coupure(id_batiment, debut_str, fin_str, cause)
        if isinstance(result, int): # Check if it's the lastrowid (success)
            self._load_coupures()
            self._clear_input_fields()
        else: # It's a tuple (False, error_message)
            success, error_message = result
            QMessageBox.warning(self, "Erreur d'Ajout", error_message)

    def _edit_coupure(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        id_coupure = int(self.table_widget.item(row, 0).text())
        id_batiment = self.batiment_combo.currentData()
        debut_str = self.debut_coupure_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        fin_datetime = self.fin_coupure_input.dateTime()
        fin_str = fin_datetime.toString("yyyy-MM-dd HH:mm:ss") if fin_datetime.isValid() else None
        cause = self.cause_input.toPlainText() or None

        if not debut_str or id_batiment is None:
            QMessageBox.warning(self, "Erreur", "Le bâtiment et la date de début sont obligatoires.")
            return
        
        # Convert to datetime objects for comparison
        debut_dt = datetime.fromisoformat(debut_str)
        fin_dt = datetime.fromisoformat(fin_str) if fin_str else None

        if fin_dt and fin_dt <= debut_dt:
            QMessageBox.warning(self, "Erreur", "La date de fin doit être postérieure à la date de début.")
            return

        # Assuming coupure_model has an update_coupure method
        success, error_message = self.coupure_model.update_coupure(id_coupure, id_batiment, debut_str, fin_str, cause)
        if success:
            self._load_coupures()
            self._clear_input_fields()
        else:
            QMessageBox.warning(self, "Erreur de Modification", error_message)

    def _delete_coupure(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, "Confirmer Suppression",
                                     "Êtes-vous sûr de vouloir supprimer cette coupure ?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            id_coupure = int(self.table_widget.item(row, 0).text())
            # Assuming coupure_model has a delete_coupure method
            success, error_message = self.coupure_model.delete_coupure(id_coupure)
            if success:
                self._load_coupures()
                self._clear_input_fields()
            else:
                QMessageBox.warning(self, "Erreur de Suppression", error_message)

    def _delete_coupure(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, "Confirmer Suppression",
                                     "Êtes-vous sûr de vouloir supprimer cette coupure ?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            id_coupure = int(self.table_widget.item(row, 0).text())
            # Assuming coupure_model has a delete_coupure method
            success, error_message = self.coupure_model.delete_coupure(id_coupure)
            if success:
                self._load_coupures()
                self._clear_input_fields()
            else:
                QMessageBox.warning(self, "Erreur de Suppression", error_message)