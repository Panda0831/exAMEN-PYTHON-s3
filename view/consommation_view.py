from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QComboBox, QMessageBox, QDateTimeEdit
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime # Import datetime for date parsing

from model.consommation_model import ConsommationModel
from model.equipement_model import EquipementModel
from model.source_model import SourceModel
from analysis.statistiques import Statistique # Import Statistique for aggregation
from view.components.matplotlib_widget import MatplotlibWidget # Import MatplotlibWidget

class ConsommationView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Suivi de Consommation")
        self.setGeometry(150, 150, 1200, 800) # Increased size for graph

        self.consommation_model = ConsommationModel()
        self.equipement_model = EquipementModel()
        self.source_model = SourceModel()
        self.statistique_analyzer = Statistique() # Instantiate Statistique

        self.main_layout = QVBoxLayout(self)

        self._create_filter_fields()
        self._create_aggregation_graph_section() # New method for graph
        self._create_table_widget()
        self._create_buttons()
        self._load_consommations()

    def _create_filter_fields(self):
        filter_layout = QHBoxLayout()

        # Date Debut
        filter_layout.addWidget(QLabel("Date Début:"))
        self.date_debut_input = QDateTimeEdit(self)
        self.date_debut_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.date_debut_input.setDateTime(QDateTime(2025, 1, 1, 0, 0, 0)) # Default to a sensible start date
        filter_layout.addWidget(self.date_debut_input)

        # Date Fin
        filter_layout.addWidget(QLabel("Date Fin:"))
        self.date_fin_input = QDateTimeEdit(self)
        self.date_fin_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.date_fin_input.setDateTime(QDateTime.currentDateTime().addDays(1)) # Default to end of today for filtering
        filter_layout.addWidget(self.date_fin_input)

        # Equipement Filter
        filter_layout.addWidget(QLabel("Équipement:"))
        self.equipement_filter_combo = QComboBox(self)
        self.equipement_filter_combo.addItem("Tous", None)
        self._load_equipements_to_combo()
        filter_layout.addWidget(self.equipement_filter_combo)

        # Source Filter
        filter_layout.addWidget(QLabel("Source:"))
        self.source_filter_combo = QComboBox(self)
        self.source_filter_combo.addItem("Toutes", None)
        self._load_sources_to_combo()
        filter_layout.addWidget(self.source_filter_combo)

        self.filter_button = QPushButton("Filtrer", self)
        self.filter_button.clicked.connect(self._load_consommations)
        filter_layout.addWidget(self.filter_button)

        self.main_layout.addLayout(filter_layout)

    def _create_aggregation_graph_section(self):
        aggregation_controls_layout = QHBoxLayout()
        aggregation_controls_layout.addWidget(QLabel("Agrégation par:"))
        self.aggregation_period_combo = QComboBox(self)
        self.aggregation_period_combo.addItem("Jour", "jour")
        self.aggregation_period_combo.addItem("Semaine", "semaine")
        self.aggregation_period_combo.addItem("Mois", "mois")
        self.aggregation_period_combo.currentTextChanged.connect(self._load_consommations)
        aggregation_controls_layout.addWidget(self.aggregation_period_combo)
        aggregation_controls_layout.addStretch() # Push combo to left

        graph_section_layout = QVBoxLayout()
        graph_section_layout.addLayout(aggregation_controls_layout)

        self.aggregation_chart = MatplotlibWidget(self)
        self.aggregation_chart.setMinimumHeight(350)
        graph_section_layout.addWidget(self.aggregation_chart)

        self.main_layout.addLayout(graph_section_layout)

    def _load_equipements_to_combo(self):
        equipements = self.equipement_model.get_all_equipements()
        for e in equipements:
            self.equipement_filter_combo.addItem(f"{e['nom_equipement']} ({e['nom_batiment']})", e["id_equipement"])

    def _load_sources_to_combo(self):
        sources = self.source_model.get_all_sources()
        for s in sources:
            self.source_filter_combo.addItem(s["nom_source"], s["id_source"])

    def _create_table_widget(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Équipement", "Source", "Date/Heure", "Durée (min)", "Énergie (kWh)", "Bâtiment"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.main_layout.addWidget(self.table_widget)

    def _create_buttons(self):
        button_layout = QHBoxLayout()
        # Add any action buttons here if needed, e.g., "Exporter"
        self.main_layout.addLayout(button_layout)

    def _load_consommations(self):
        self.table_widget.setRowCount(0)
        
        # Get filter values
        date_debut_str = self.date_debut_input.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.date_debut_input.dateTime().isValid() else None
        date_fin_str = self.date_fin_input.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.date_fin_input.dateTime().isValid() else None
        selected_equipement_id = self.equipement_filter_combo.currentData()
        selected_source_id = self.source_filter_combo.currentData()
        selected_period = self.aggregation_period_combo.currentData() # Get selected period

        all_consos_raw = self.consommation_model.get_all_consommation()
        
        filtered_consos_for_table = []
        filtered_consos_for_graph = [] # Data in (date_time_obj, energie_kwh) format

        for conso in all_consos_raw:
            match = True
            
            # Filter by Equipement
            if selected_equipement_id is not None and conso["id_equipement"] != selected_equipement_id:
                match = False
            # Filter by Source
            if selected_source_id is not None and conso["id_source"] != selected_source_id:
                match = False

            # Convert date_heure to datetime object for proper comparison and aggregation
            conso_datetime = datetime.fromisoformat(conso["date_heure"])
            
            # Filter by Date (using datetime objects)
            if date_debut_str:
                try:
                    date_debut_dt = datetime.fromisoformat(date_debut_str)
                    if conso_datetime < date_debut_dt:
                        match = False
                except ValueError:
                    pass # Invalid date format, skip filter
            
            if date_fin_str:
                try:
                    date_fin_dt = datetime.fromisoformat(date_fin_str)
                    if conso_datetime > date_fin_dt:
                        match = False
                except ValueError:
                    pass # Invalid date format, skip filter
            
            if match:
                filtered_consos_for_table.append(conso)
                filtered_consos_for_graph.append((conso_datetime, conso["energie_kwh"]))


        # Populate table
        self.table_widget.setRowCount(len(filtered_consos_for_table))
        for row, conso in enumerate(filtered_consos_for_table):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(conso["id_conso"])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(conso["nom_equipement"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(conso["nom_source"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(conso["date_heure"]))
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(conso["duree_minutes"])))
            self.table_widget.setItem(row, 5, QTableWidgetItem(str(conso["energie_kwh"])))
            self.table_widget.setItem(row, 6, QTableWidgetItem(conso["batiment"]))
        
        # Draw aggregation graph
        self._draw_aggregation_graph(filtered_consos_for_graph, selected_period)

    def _draw_aggregation_graph(self, consommations, periode):
        fig = self.aggregation_chart.get_figure()
        fig.clear()
        ax = fig.add_subplot(111)

        if not consommations:
            ax.text(0.5, 0.5, "Aucune donnée de consommation\nà afficher pour le graphique", ha='center', va='center', transform=ax.transAxes)
        else:
            # Aggregate data using Statistique analyzer
            aggregated_data = self.statistique_analyzer.agreger_par_periode(consommations, periode=periode)

            dates = list(aggregated_data.keys())
            energies = list(aggregated_data.values())

            ax.bar(dates, energies, color='green')
            ax.set_xlabel(f"{periode.capitalize()}")
            ax.set_ylabel("Consommation Totale (kWh)")
            ax.set_title(f"Consommation Totale par {periode.capitalize()}")
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        fig.tight_layout()
        self.aggregation_chart.canvas.draw_idle()

if __name__ == '__main__':
    import sys
    import os
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    sys.path.insert(0, project_root)

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    view = ConsommationView()
    view.exec()
    sys.exit(app.exec())
