from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QComboBox, QMessageBox, QWidget, QDateTimeEdit
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime

from model.coupure_model import CoupureModel
from model.batiment_model import BatimentModel
from view.components.matplotlib_widget import MatplotlibWidget # For potential future graphs

class CoupuresHistoryView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique des Coupures")
        self.setGeometry(100, 100, 1000, 700)

        self.coupure_model = CoupureModel()
        self.batiment_model = BatimentModel()

        self.main_layout = QVBoxLayout(self)

        self._create_filter_fields()
        self._create_history_table()
        # self._create_history_graph() # Optional: for future graph
        self._load_coupure_history()

    def _create_filter_fields(self):
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Date Début:"))
        self.date_debut_input = QDateTimeEdit(self)
        self.date_debut_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.date_debut_input.setDateTime(QDateTime(2025, 1, 1, 0, 0, 0)) # Default to a sensible start date
        filter_layout.addWidget(self.date_debut_input)

        filter_layout.addWidget(QLabel("Date Fin:"))
        self.date_fin_input = QDateTimeEdit(self)
        self.date_fin_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.date_fin_input.setDateTime(QDateTime.currentDateTime().addDays(1)) # Default to end of today for filtering
        filter_layout.addWidget(self.date_fin_input)

        filter_layout.addWidget(QLabel("Bâtiment:"))
        self.batiment_filter_combo = QComboBox(self)
        self.batiment_filter_combo.addItem("Tous", None)
        self._load_batiments_to_combo()
        filter_layout.addWidget(self.batiment_filter_combo)

        self.filter_button = QPushButton("Filtrer", self)
        self.filter_button.clicked.connect(self._load_coupure_history)
        filter_layout.addWidget(self.filter_button)

        self.main_layout.addLayout(filter_layout)

    def _load_batiments_to_combo(self):
        batiments = self.batiment_model.get_all_batiments()
        for b in batiments:
            self.batiment_filter_combo.addItem(b["nom"], b["id_batiment"])

    def _create_history_table(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Bâtiment", "Début", "Fin", "Cause"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.main_layout.addWidget(self.table_widget)

    def _load_coupure_history(self):
        self.table_widget.setRowCount(0)
        
        date_debut_str = self.date_debut_input.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.date_debut_input.dateTime().isValid() else None
        date_fin_str = self.date_fin_input.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.date_fin_input.dateTime().isValid() else None
        selected_batiment_id = self.batiment_filter_combo.currentData()

        all_coupures = self.coupure_model.get_all_coupures()
        
        filtered_coupures = []
        for coupure in all_coupures:
            match = True
            
            # Filter by Batiment
            if selected_batiment_id is not None and coupure["id_batiment"] != selected_batiment_id:
                match = False

            # Convert debut_coupure to datetime object for proper comparison
            coupure_debut_dt = datetime.fromisoformat(coupure["debut_coupure"])
            
            # Filter by Date
            if date_debut_str:
                try:
                    date_debut_dt = datetime.fromisoformat(date_debut_str)
                    if coupure_debut_dt < date_debut_dt:
                        match = False
                except ValueError:
                    pass
            
            if date_fin_str:
                try:
                    date_fin_dt = datetime.fromisoformat(date_fin_str)
                    if coupure_debut_dt > date_fin_dt:
                        match = False
                except ValueError:
                    pass
            
            if match:
                filtered_coupures.append(coupure)

        # Populate table
        self.table_widget.setRowCount(len(filtered_coupures))
        for row, cp in enumerate(filtered_coupures):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(cp["id_coupure"])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(cp["nom_batiment"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(cp["debut_coupure"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(cp["fin_coupure"] or "En cours"))
            self.table_widget.setItem(row, 4, QTableWidgetItem(cp["cause"] or "N/A"))


if __name__ == '__main__':
    import sys
    import os
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    sys.path.insert(0, project_root)

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    view = CoupuresHistoryView()
    view.exec()
    sys.exit(app.exec())