from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QMessageBox
from PySide6.QtCore import Qt

from model.source_model import SourceModel

class SourceView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Sources d'Énergie")
        self.setGeometry(250, 250, 700, 500)

        self.source_model = SourceModel()

        self.main_layout = QVBoxLayout(self)

        self._create_input_fields()
        self._create_table_widget()
        self._create_buttons()
        self._load_sources()

    def _create_input_fields(self):
        input_layout = QHBoxLayout()

        self.nom_source_input = QLineEdit(self)
        self.nom_source_input.setPlaceholderText("Nom de la source")
        input_layout.addWidget(QLabel("Nom:"))
        input_layout.addWidget(self.nom_source_input)

        self.cout_kwh_input = QLineEdit(self)
        self.cout_kwh_input.setPlaceholderText("Coût (Ariary/kWh)")
        input_layout.addWidget(QLabel("Coût (Ariary/kWh):"))
        input_layout.addWidget(self.cout_kwh_input)
        
        self.description_input = QLineEdit(self)
        self.description_input.setPlaceholderText("Description")
        input_layout.addWidget(QLabel("Description:"))
        input_layout.addWidget(self.description_input)

        self.main_layout.addLayout(input_layout)

    def _create_table_widget(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Nom", "Coût (Ariary/kWh)", "Description"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.table_widget.itemSelectionChanged.connect(self._selection_changed)
        self.main_layout.addWidget(self.table_widget)

    def _create_buttons(self):
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter", self)
        self.add_button.clicked.connect(self._add_source)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Modifier", self)
        self.edit_button.clicked.connect(self._edit_source)
        self.edit_button.setEnabled(False) # Disable until an item is selected
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Supprimer", self)
        self.delete_button.clicked.connect(self._delete_source)
        self.delete_button.setEnabled(False) # Disable until an item is selected
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

    def _load_sources(self):
        self.table_widget.setRowCount(0)
        sources = self.source_model.get_all_sources()
        self.table_widget.setRowCount(len(sources))
        for row, source in enumerate(sources):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(source["id_source"])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(source["nom_source"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(source["cout_kwh"])))
            self.table_widget.setItem(row, 3, QTableWidgetItem(source["description"]))

    def _selection_changed(self):
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            row = selected_items[0].row()
            self.nom_source_input.setText(self.table_widget.item(row, 1).text())
            self.cout_kwh_input.setText(self.table_widget.item(row, 2).text())
            self.description_input.setText(self.table_widget.item(row, 3).text())
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self._clear_input_fields()

    def _clear_input_fields(self):
        self.nom_source_input.clear()
        self.cout_kwh_input.clear()
        self.description_input.clear()

    def _add_source(self):
        nom = self.nom_source_input.text()
        cout_str = self.cout_kwh_input.text()
        description = self.description_input.text()

        if not nom or not cout_str:
            QMessageBox.warning(self, "Erreur", "Le nom et le coût sont obligatoires.")
            return

        try:
            cout = float(cout_str)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Le coût doit être un nombre valide.")
            return
        
        if self.source_model.add_source(nom, cout, description):
            self._load_sources()
            self._clear_input_fields()
        else:
            QMessageBox.warning(self, "Erreur d'Ajout", f"Impossible d'ajouter la source '{nom}'. Elle pourrait déjà exister ou une erreur de base de données est survenue.")

    def _edit_source(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        id_source = int(self.table_widget.item(row, 0).text())
        nom = self.nom_source_input.text()
        cout_str = self.cout_kwh_input.text()
        description = self.description_input.text()

        if not nom or not cout_str:
            QMessageBox.warning(self, "Erreur", "Le nom et le coût sont obligatoires.")
            return

        try:
            cout = float(cout_str)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Le coût doit être un nombre valide.")
            return

        # Update model
        success, error_message = self.source_model.update_source(id_source, nom, cout, description)
        if success:
            self._load_sources()
            self._clear_input_fields()
        else:
            QMessageBox.warning(self, "Erreur de Modification", error_message)

    def _delete_source(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, "Confirmer Suppression",
                                     "Êtes-vous sûr de vouloir supprimer cette source ?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            id_source = int(self.table_widget.item(row, 0).text())
            # Assuming SourceModel has a delete_source method
            if self.source_model.delete_source(id_source):
                self._load_sources()
                self._clear_input_fields()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de supprimer la source. Elle est peut-être utilisée ailleurs.")
