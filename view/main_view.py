from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGridLayout, QComboBox
from PySide6.QtCore import Qt, Signal

# Import actual MainChart component
from view.components.main_chart import MainChart
from view.components.sidebar_stats import SidebarStats
from view.components.cards_frame import CardsFrame
from view.components.alerts_table import AlertsTable
from model.batiment_model import BatimentModel


class MainView(QMainWindow):
    manage_equipements_triggered = Signal() # Define the signal
    manage_sources_triggered = Signal() # Define the new signal
    manage_coupures_triggered = Signal() # Define the new signal
    add_consommation_triggered = Signal() # Define the new signal
    show_consommation_view_triggered = Signal() # Define the new signal
    show_couts_view_triggered = Signal() # Define the new signal
    show_efficacite_view_triggered = Signal() # Define the new signal
    show_anomalies_view_triggered = Signal() # Define the new signal
    show_alertes_view_triggered = Signal() # Define the new signal
    show_coupures_history_view_triggered = Signal() # Define the new signal
    show_simulation_view_triggered = Signal() # Define the new signal
    refresh_all_triggered = Signal() # New signal for refreshing all components

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartEnergyMG - Gestion Intelligente de l'Énergie")
        self.setGeometry(100, 100, 1400, 900) # x, y, width, height (Increased size for layout)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QGridLayout(self.central_widget) # Use QGridLayout

        # Adjust stretch factors for better visual balance
        self.main_layout.setRowStretch(0, 1) # CardsFrame
        self.main_layout.setRowStretch(1, 1) # Building selector
        self.main_layout.setRowStretch(2, 3) # MainChart & SidebarStats
        self.main_layout.setRowStretch(3, 2) # AlertsTable

        self.main_layout.setColumnStretch(0, 0.6) # MainChart
        self.main_layout.setColumnStretch(1, 1.9) # SidebarStats (1.9 times wider than MainChart)


        # Zone: Haut (Row 0, Span all columns)
        self.cards_frame = CardsFrame(self)
        self.main_layout.addWidget(self.cards_frame, 0, 0, 1, 2) # row, col, rowSpan, colSpan

        # Zone: Building Selector (Row 1, Span all columns)
        building_selector_layout = QHBoxLayout()
        building_selector_layout.addWidget(QLabel("Sélectionner un bâtiment:"))
        self.building_combo = QComboBox(self)
        building_selector_layout.addWidget(self.building_combo)
        self.main_layout.addLayout(building_selector_layout, 1, 0, 1, 2) # row, col, rowSpan, colSpan

        # Zone: Gauche (Row 2, Column 0)
        self.main_chart = MainChart(self)
        self.main_layout.addWidget(self.main_chart, 2, 0)

        # Zone: Droite (Row 2, Column 1)
        self.sidebar_stats = SidebarStats(self)
        self.main_layout.addWidget(self.sidebar_stats, 2, 1)

        # Zone: Bas (Row 3, Span all columns)
        self.alerts_table = AlertsTable(self)
        self.main_layout.addWidget(self.alerts_table, 3, 0, 1, 2)
        
        self._create_menu_bar()
        self._load_batiments_to_combo()
        self.building_combo.currentIndexChanged.connect(self._on_building_selected)
        self.refresh_all_triggered.connect(self._refresh_dashboard_components) # Connect signal to internal method
        self._refresh_dashboard_components() # Initial refresh

    def _load_batiments_to_combo(self):
        self.building_combo.clear()
        self.building_combo.addItem("Tous les bâtiments", None)
        batiment_model = BatimentModel()
        batiments = batiment_model.get_all_batiments()
        for b in batiments:
            self.building_combo.addItem(b["nom"], b["id_batiment"])

    def _on_building_selected(self):
        self._refresh_dashboard_components()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        # Menu Fichier
        file_menu = menu_bar.addMenu("Fichier")
        file_menu.addAction("Quitter", self.close)
        
        refresh_action = file_menu.addAction("Tout Rafraîchir") # New action
        refresh_action.triggered.connect(self.refresh_all_triggered.emit) # Connect action to emit signal

        # Menu Analyse
        analyse_menu = menu_bar.addMenu("Analyse")
        show_consommation_action = analyse_menu.addAction("Consommation Globale") # New action
        show_consommation_action.triggered.connect(self.show_consommation_view_triggered.emit)
        
        show_couts_action = analyse_menu.addAction("Coûts Énergétiques") # New action
        show_couts_action.triggered.connect(self.show_couts_view_triggered.emit)

        show_efficacite_action = analyse_menu.addAction("Efficacité & Gaspillage") # New action
        show_efficacite_action.triggered.connect(self.show_efficacite_view_triggered.emit)

        show_anomalies_action = analyse_menu.addAction("Anomalies") # New action
        show_anomalies_action.triggered.connect(self.show_anomalies_view_triggered.emit)
        
        show_alertes_action = analyse_menu.addAction("Alertes Énergétiques") # New action
        show_alertes_action.triggered.connect(self.show_alertes_view_triggered.emit)

        show_coupures_history_action = analyse_menu.addAction("Historique des Coupures") # New action
        show_coupures_history_action.triggered.connect(self.show_coupures_history_view_triggered.emit)

        show_simulation_action = analyse_menu.addAction("Simulation de Coupure") # New action
        show_simulation_action.triggered.connect(self.show_simulation_view_triggered.emit)

        # Menu Données
        data_menu = menu_bar.addMenu("Données")
        manage_equipements_action = data_menu.addAction("Gérer Équipements")
        manage_equipements_action.triggered.connect(self.manage_equipements_triggered.emit)
        
        manage_sources_action = data_menu.addAction("Gérer Sources") # New action
        manage_sources_action.triggered.connect(self.manage_sources_triggered.emit)

        manage_coupures_action = data_menu.addAction("Gérer Coupures") # New action
        manage_coupures_action.triggered.connect(self.manage_coupures_triggered.emit)

        add_consommation_action = data_menu.addAction("Ajouter Consommation") # New action
        add_consommation_action.triggered.connect(self.add_consommation_triggered.emit)

        # Menu Aide
        help_menu = menu_bar.addMenu("Aide")
        help_menu.addAction("À propos")

    def _refresh_dashboard_components(self):
        building_id = self.building_combo.currentData()
        # Refresh CardsFrame
        self.cards_frame.update_data()
        # Refresh MainChart
        self.main_chart.draw_chart(building_id)
        # Refresh SidebarStats
        self.sidebar_stats.draw_charts()
        # Refresh AlertsTable
        self.alerts_table.populate_data()
