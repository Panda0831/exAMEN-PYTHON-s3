from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from analysis.couts import Couts
from analysis.statistiques import Statistique
from model.coupure_model import CoupureModel
from config.colors import AppColors # Import AppColors

class CardWidget(QWidget):
    """A reusable widget to display a title and a value, styled as a card."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.value_label = QLabel("N/A")
        self.value_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.value_label)
        
        self.setStyleSheet(f"""
            CardWidget {{
                border: 1px solid {AppColors.MidGray}; /* Use AppColors */
                border-radius: 8px;
                background-color: {AppColors.White}; /* Use AppColors */
                padding: 10px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.05); /* Subtle shadow */
            }}
        """)

    def set_value(self, value):
        self.value_label.setText(str(value))

class CardsFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(20)

        self.source_card = CardWidget("Source Actuelle")
        self.cost_card = CardWidget("Coût Mensuel Total")
        self.alerts_card = CardWidget("Alertes Actuelles")
        
        self.layout.addWidget(self.source_card)
        self.layout.addWidget(self.cost_card)
        self.layout.addWidget(self.alerts_card)

        # Initialize models and analyzers
        self.coupure_model = CoupureModel()
        self.couts_analyzer = Couts()
        self.statistique_analyzer = Statistique()
        
    def update_data(self):
        # 1. Update Current Source Status
        # Simplified: Check for ongoing coupures. If yes, Groupe, else JIRAMA.
        current_coupures = self.coupure_model.get_current_coupures()
        current_source = "Groupe électrogène" if current_coupures else "JIRAMA"
        self.source_card.set_value(current_source)
        
        # 2. Update Total Monthly Cost
        couts_par_mois = self.couts_analyzer.calculer_cout_par_periode(periode='mois')
        # Assuming we are in the current month
        current_month_key = list(couts_par_mois.keys())[-1] if couts_par_mois else "N/A"
        total_cost_month = f"{couts_par_mois.get(current_month_key, 0):,.2f} Ariary"
        self.cost_card.set_value(total_cost_month)
        
        # 3. Update Critical Alerts Count
        # (ongoing coupures + anomalies)
        num_ongoing_coupures = len(current_coupures)
        num_anomalies = len(self.statistique_analyzer.anomalies())
        total_alerts = num_ongoing_coupures + num_anomalies
        self.alerts_card.set_value(total_alerts)
        
        # Style alerts card based on value
        if total_alerts > 0:
            self.alerts_card.value_label.setStyleSheet(f"color: {AppColors.Danger};") # Use AppColors.Danger
        else:
            self.alerts_card.value_label.setStyleSheet(f"color: {AppColors.Success};") # Use AppColors.Success
