from PySide6.QtWidgets import QApplication
from view.main_view import MainView
from view.equipement_view import EquipementView # Import EquipementView
from view.source_view import SourceView # Import SourceView
from view.coupure_view import CoupureView # Import CoupureView
from view.consommation_add_view import ConsommationAddView # Import ConsommationAddView
from view.consommation_view import ConsommationView # Import ConsommationView
from view.couts_view import CoutsView # Import CoutsView
from view.efficacite_view import EfficaciteView # Import EfficaciteView
from view.anomalies_view import AnomaliesView # Import AnomaliesView
from view.alertes_view import AlertesView # Import AlertesView
from view.coupures_history_view import CoupuresHistoryView # Import CoupuresHistoryView
from view.simulation_view import SimulationView # Import SimulationView

class MainController:
    def __init__(self, app_instance):
        self.app = app_instance # Use the passed app instance
        self.main_view = MainView()
        self.main_view.manage_equipements_triggered.connect(self.show_equipement_view) # Connect signal to slot
        self.main_view.manage_sources_triggered.connect(self.show_source_view) # Connect new signal
        self.main_view.manage_coupures_triggered.connect(self.show_coupure_view) # Connect new signal
        self.main_view.add_consommation_triggered.connect(self.show_add_consommation_view) # Connect new signal
        self.main_view.show_consommation_view_triggered.connect(self.show_consommation_view) # Connect new signal
        self.main_view.show_couts_view_triggered.connect(self.show_couts_view) # Connect new signal
        self.main_view.show_efficacite_view_triggered.connect(self.show_efficacite_view) # Connect new signal
        self.main_view.show_anomalies_view_triggered.connect(self.show_anomalies_view) # Connect new signal
        self.main_view.show_alertes_view_triggered.connect(self.show_alertes_view) # Connect new signal
        self.main_view.show_coupures_history_view_triggered.connect(self.show_coupures_history_view) # Connect new signal
        self.main_view.show_simulation_view_triggered.connect(self.show_simulation_view) # Connect new signal

        # Ici, nous pourrions instancier nos modèles et modules d'analyse
        # et les passer à la vue ou les gérer directement pour les interactions.
        # self.consommation_model = ConsommationModel()
        # self.statistique_analyzer = Statistique()
        # etc.

    def show_equipement_view(self):
        self.equipement_view = EquipementView(self.main_view) # Pass main_view as parent
        self.equipement_view.exec() # Use exec_() for modal dialog

    def show_source_view(self):
        self.source_view = SourceView(self.main_view) # Pass main_view as parent
        self.source_view.exec() # Use exec_() for modal dialog

    def show_coupure_view(self):
        self.coupure_view = CoupureView(self.main_view) # Pass main_view as parent
        self.coupure_view.exec() # Use exec_() for modal dialog
    
    def show_add_consommation_view(self):
        self.consommation_add_view = ConsommationAddView(self.main_view) # Pass main_view as parent
        self.consommation_add_view.exec() # Use exec_() for modal dialog

    def show_consommation_view(self):
        self.consommation_view = ConsommationView(self.main_view) # Pass main_view as parent
        self.consommation_view.exec() # Use exec_() for modal dialog

    def show_couts_view(self):
        self.couts_view = CoutsView(self.main_view) # Pass main_view as parent
        self.couts_view.exec() # Use exec_() for modal dialog

    def show_efficacite_view(self):
        self.efficacite_view = EfficaciteView(self.main_view) # Pass main_view as parent
        self.efficacite_view.exec() # Use exec_() for modal dialog

    def show_anomalies_view(self):
        self.anomalies_view = AnomaliesView(self.main_view) # Pass main_view as parent
        self.anomalies_view.exec() # Use exec_() for modal dialog

    def show_alertes_view(self):
        self.alertes_view = AlertesView(self.main_view) # Pass main_view as parent
        self.alertes_view.exec() # Use exec_() for modal dialog

    def show_coupures_history_view(self):
        self.coupures_history_view = CoupuresHistoryView(self.main_view) # Pass main_view as parent
        self.coupures_history_view.exec() # Use exec_() for modal dialog

    def show_simulation_view(self):
        self.simulation_view = SimulationView(self.main_view) # Pass main_view as parent
        self.simulation_view.exec() # Use exec_() for modal dialog

    def run(self):
        self.main_view.show()
        self.app.exec()
