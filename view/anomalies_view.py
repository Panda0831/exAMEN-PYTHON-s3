from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QComboBox, QMessageBox, QWidget
from PySide6.QtCore import Qt, QDateTime

from model.consommation_model import ConsommationModel
from model.equipement_model import EquipementModel
from model.source_model import SourceModel
from analysis.statistiques import Statistique
from view.components.matplotlib_widget import MatplotlibWidget
from datetime import datetime

class AnomaliesView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Détection et Suivi des Anomalies")
        self.setGeometry(100, 100, 1200, 800)

        self.consommation_model = ConsommationModel()
        self.equipement_model = EquipementModel()
        self.source_model = SourceModel()
        self.statistique_analyzer = Statistique()

        self.main_layout = QVBoxLayout(self)

        self._create_filter_fields()
        self._create_anomalies_chart_section()
        self._create_anomalies_table()
        self._create_buttons() # For potential actions like "Mark as reviewed"

        self._load_anomalies()

    def _create_filter_fields(self):
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Date Début:"))
        self.date_debut_input = QLineEdit(self)
        self.date_debut_input.setPlaceholderText("YYYY-MM-DD HH:MM:SS")
        filter_layout.addWidget(self.date_debut_input)

        filter_layout.addWidget(QLabel("Date Fin:"))
        self.date_fin_input = QLineEdit(self)
        self.date_fin_input.setPlaceholderText("YYYY-MM-DD HH:MM:SS")
        filter_layout.addWidget(self.date_fin_input)

        filter_layout.addWidget(QLabel("Équipement:"))
        self.equipement_filter_combo = QComboBox(self)
        self.equipement_filter_combo.addItem("Tous", None)
        self._load_equipements_to_combo()
        filter_layout.addWidget(self.equipement_filter_combo)

        filter_layout.addWidget(QLabel("Source:"))
        self.source_filter_combo = QComboBox(self)
        self.source_filter_combo.addItem("Toutes", None)
        self._load_sources_to_combo()
        filter_layout.addWidget(self.source_filter_combo)

        self.filter_button = QPushButton("Filtrer", self)
        self.filter_button.clicked.connect(self._load_anomalies)
        filter_layout.addWidget(self.filter_button)

        self.main_layout.addLayout(filter_layout)

    def _load_equipements_to_combo(self):
        equipements = self.equipement_model.get_all_equipements()
        for e in equipements:
            self.equipement_filter_combo.addItem(f"{e['nom_equipement']} ({e['nom_batiment']})", e["id_equipement"])

    def _load_sources_to_combo(self):
        sources = self.source_model.get_all_sources()
        for s in sources:
            self.source_filter_combo.addItem(s["nom_source"], s["id_source"])

    def _create_anomalies_chart_section(self):
        self.anomalies_chart = MatplotlibWidget(self)
        self.anomalies_chart.setMinimumHeight(400)
        self.main_layout.addWidget(self.anomalies_chart)

    def _create_anomalies_table(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["ID Conso", "Équipement", "Source", "Date/Heure", "Énergie (kWh)", "Z-score"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.main_layout.addWidget(self.table_widget)

    def _create_buttons(self):
        button_layout = QHBoxLayout()
        # Example: self.mark_reviewed_button = QPushButton("Marquer comme revues")
        # button_layout.addWidget(self.mark_reviewed_button)
        self.main_layout.addLayout(button_layout)

    def _load_anomalies(self):
        self.table_widget.setRowCount(0)
        
        date_debut_str = self.date_debut_input.text() or None
        date_fin_str = self.date_fin_input.text() or None
        selected_equipement_id = self.equipement_filter_combo.currentData()
        selected_source_id = self.source_filter_combo.currentData()

        all_consos_raw = self.consommation_model.get_all_consommation()
        
        filtered_consos_for_table = []
        
        # Anomalies data from Statistique analyzer
        all_anomalies_raw = self.statistique_analyzer.anomalies(facteur=2) # Using default factor for now

        filtered_anomalies = []
        
        for anomaly in all_anomalies_raw:
            match = True
            
            # Filter by Equipement
            if selected_equipement_id is not None and anomaly["id_equipement"] != selected_equipement_id:
                match = False
            # Filter by Source
            if selected_source_id is not None and anomaly["id_source"] != selected_source_id:
                match = False

            # Convert date_heure to datetime object for proper comparison and aggregation
            conso_datetime = datetime.fromisoformat(anomaly["date_heure"])
            
            # Filter by Date (using datetime objects)
            if date_debut_str:
                try:
                    date_debut_dt = datetime.fromisoformat(date_debut_str)
                    if conso_datetime < date_debut_dt:
                        match = False
                except ValueError:
                    pass
            
            if date_fin_str:
                try:
                    date_fin_dt = datetime.fromisoformat(date_fin_str)
                    if conso_datetime > date_fin_dt:
                        match = False
                except ValueError:
                    pass
            
            if match:
                filtered_anomalies.append(anomaly)
                
        # Populate table
        self.table_widget.setRowCount(len(filtered_anomalies))
        for row, anomaly in enumerate(filtered_anomalies):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(anomaly["id_conso"])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(anomaly["nom_equipement"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(anomaly["nom_source"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(anomaly["date_heure"]))
            self.table_widget.setItem(row, 4, QTableWidgetItem(f"{anomaly['energie_kwh']:.2f}"))
            # Z-score calculation might be needed here or passed from Statistique
            self.table_widget.setItem(row, 5, QTableWidgetItem("N/A")) # Placeholder for Z-score

        # Draw chart
        self._draw_anomalies_chart(all_consos_raw, filtered_anomalies)

    def _draw_anomalies_chart(self, all_consos, anomalies_to_highlight):
        fig = self.anomalies_chart.get_figure()
        fig.clear()
        ax = fig.add_subplot(111)

        if not all_consos:
            ax.text(0.5, 0.5, "Aucune donnée de consommation\nà afficher pour les anomalies", ha='center', va='center', transform=ax.transAxes)
            fig.tight_layout()
            self.anomalies_chart.canvas.draw_idle()
            return
            
        all_consos.sort(key=lambda x: datetime.fromisoformat(x['date_heure']))
        
        dates = [datetime.fromisoformat(item['date_heure']) for item in all_consos]
        energies = [item['energie_kwh'] for item in all_consos]
        
        # Prepare anomaly data for plotting
        anomaly_dates = [datetime.fromisoformat(item['date_heure']) for item in anomalies_to_highlight]
        anomaly_energies = [item['energie_kwh'] for item in anomalies_to_highlight]

        ax.plot(dates, energies, label='Consommation Normale', color='blue', alpha=0.7, zorder=1)
        ax.scatter(anomaly_dates, anomaly_energies, color='red', s=100,
                    label='Anomalies Détectées', zorder=2, edgecolors='black')

        ax.set_xlabel("Date et Heure")
        ax.set_ylabel("Consommation (kWh)")
        ax.set_title("Détection d'Anomalies de Consommation")
        ax.legend()
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        fig.autofmt_xdate()
        fig.tight_layout()
        self.anomalies_chart.canvas.draw_idle()

if __name__ == '__main__':
    import sys
    import os
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    sys.path.insert(0, project_root)

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    view = AnomaliesView()
    view.exec()
    sys.exit(app.exec())
