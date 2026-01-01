from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox, QDateTimeEdit
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime, timedelta

from analysis.couts import Couts
from model.consommation_model import ConsommationModel # To get average consumption

class SimulationView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulation de Coupure JIRAMA")
        self.setGeometry(300, 300, 600, 400)

        self.couts_analyzer = Couts()
        self.consommation_model = ConsommationModel() # To get average consumption

        self.main_layout = QVBoxLayout(self)

        self._create_input_fields()
        self._create_buttons()
        self._create_result_display()

    def _create_input_fields(self):
        # Date/Heure de début de coupure
        self.start_datetime_input = QDateTimeEdit(self) # Replaced QLineEdit with QDateTimeEdit
        self.start_datetime_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss") # Set display format
        self.start_datetime_input.setDateTime(QDateTime.currentDateTime()) # Default to current time
        self.main_layout.addWidget(QLabel("Date/Heure de Début de Coupure:"))
        self.main_layout.addWidget(self.start_datetime_input)

        # Durée estimée
        self.duration_input = QLineEdit(self)
        self.duration_input.setPlaceholderText("Durée estimée (heures)")
        self.main_layout.addWidget(QLabel("Durée Estimée (heures):"))
        self.main_layout.addWidget(self.duration_input)

    def _create_buttons(self):
        button_layout = QHBoxLayout()
        self.simulate_button = QPushButton("Simuler Impact", self)
        self.simulate_button.clicked.connect(self._simulate_impact)
        button_layout.addWidget(self.simulate_button)

        self.close_button = QPushButton("Fermer", self)
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)
        self.main_layout.addLayout(button_layout)

    def _create_result_display(self):
        self.result_label = QLabel("Coût supplémentaire estimé: N/A")
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.result_label)

    def _simulate_impact(self):
        start_datetime = self.start_datetime_input.dateTime().toPython() # Get QDateTime and convert to Python datetime
        duration_str = self.duration_input.text()

        if not duration_str: # start_datetime will always be valid from QDateTimeEdit
            QMessageBox.warning(self, "Erreur", "La durée estimée est obligatoire.")
            return

        try:
            duration_hours = float(duration_str)
            if duration_hours <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erreur", "La durée doit être un nombre positif (heures).")
            return
        
        # Call the simulation logic in Couts analyzer
        estimated_cost, error_message = self.couts_analyzer.simuler_impact_coupure(start_datetime, duration_hours)

        if estimated_cost is not None:
            self.result_label.setText(f"Coût supplémentaire estimé: {estimated_cost:.2f} Ariary")
            self.result_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
        else:
            self.result_label.setText(f"Erreur de simulation: {error_message}")
            self.result_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")

if __name__ == '__main__':
    import sys
    import os
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    sys.path.insert(0, project_root)

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    view = SimulationView()
    view.exec()
    sys.exit(app.exec())
