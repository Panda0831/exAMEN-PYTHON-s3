from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QComboBox, QMessageBox, QWidget, QDateTimeEdit
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QColor # Import QColor
from datetime import datetime, timedelta

from model.coupure_model import CoupureModel
from analysis.statistiques import Statistique
from analysis.efficacite import Efficacite # For new analysis type

class AlertesView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alertes Énergétiques")
        self.setGeometry(100, 100, 1000, 700)

        self.coupure_model = CoupureModel()
        self.statistique_analyzer = Statistique()
        self.efficacite_analyzer = Efficacite() # Instantiate Efficacite for new analysis

        self.main_layout = QVBoxLayout(self)

        self._create_filter_fields()
        self._create_alerts_table()
        self._create_buttons() # For potential actions like "Mark as reviewed"

        self._load_alerts()

    def _create_filter_fields(self):
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Date Début:"))
        self.date_debut_input = QDateTimeEdit(self)
        self.date_debut_input.setDisplayFormat("yyyy-MM-DD HH:mm:ss")
        filter_layout.addWidget(self.date_debut_input)

        filter_layout.addWidget(QLabel("Date Fin:"))
        self.date_fin_input = QDateTimeEdit(self)
        self.date_fin_input.setDisplayFormat("yyyy-MM-DD HH:mm:ss")
        self.date_fin_input.setDateTime(QDateTime.currentDateTime().addDays(1)) # Default to end of today for filtering
        filter_layout.addWidget(self.date_fin_input)

        filter_layout.addWidget(QLabel("Type d'Alerte:"))
        self.alert_type_combo = QComboBox(self)
        self.alert_type_combo.addItem("Tous", None)
        self.alert_type_combo.addItem("Coupure", "Coupure")
        self.alert_type_combo.addItem("Anomalie Consommation", "Anomalie Consommation")
        self.alert_type_combo.addItem("Gaspillage Équipement", "Gaspillage Équipement") # From Efficacite
        self.alert_type_combo.addItem("Conso. pdt Coupure", "Conso. pdt Coupure") # New analysis
        filter_layout.addWidget(self.alert_type_combo)
        
        filter_layout.addWidget(QLabel("Statut:"))
        self.status_combo = QComboBox(self)
        self.status_combo.addItem("Tous", None)
        self.status_combo.addItem("Actif", "Actif")
        self.status_combo.addItem("Résolu", "Résolu")
        filter_layout.addWidget(self.status_combo)


        self.filter_button = QPushButton("Filtrer", self)
        self.filter_button.clicked.connect(self._load_alerts)
        filter_layout.addWidget(self.filter_button)

        self.main_layout.addLayout(filter_layout)

    def _create_alerts_table(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Date", "Type", "Source", "Équipement/Bâtiment", "Description", "Statut"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.main_layout.addWidget(self.table_widget)

    def _create_buttons(self):
        button_layout = QHBoxLayout()
        # Example: self.mark_resolved_button = QPushButton("Marquer comme résolue")
        # button_layout.addWidget(self.mark_resolved_button)
        self.main_layout.addLayout(button_layout)

    def _load_alerts(self):
        self.table_widget.setRowCount(0)
        
        date_debut_str = self.date_debut_input.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.date_debut_input.dateTime().isValid() else None
        date_fin_str = self.date_fin_input.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.date_fin_input.dateTime().isValid() else None
        selected_alert_type = self.alert_type_combo.currentData()
        selected_status = self.status_combo.currentData()

        all_alerts = []

        # 1. Coupures
        coupures = self.coupure_model.get_all_coupures()
        for cp in coupures:
            alert_type = "Coupure"
            status = "Actif" if cp["fin_coupure"] is None else "Résolu"
            description = f"Coupure à {cp['nom_batiment']}. Cause: {cp['cause'] or 'N/A'}"
            alert_date = datetime.fromisoformat(cp["debut_coupure"])

            all_alerts.append({
                "date": alert_date,
                "type": alert_type,
                "source": "N/A", # Coupures don't have a source
                "equip_bat": cp["nom_batiment"],
                "description": description,
                "status": status
            })

        # 2. Anomalies Consommation (from Statistique)
        anomalies_conso = self.statistique_analyzer.anomalies() # Using default factor
        for ano in anomalies_conso:
            alert_type = "Anomalie Consommation"
            status = "Actif" # Anomalies are usually "active" until reviewed
            description = f"Pic de consommation: {ano['energie_kwh']:.2f} kWh sur {ano['nom_equipement']}"
            alert_date = datetime.fromisoformat(ano["date_heure"])
            
            all_alerts.append({
                "date": alert_date,
                "type": alert_type,
                "source": ano["nom_source"],
                "equip_bat": ano["nom_equipement"],
                "description": description,
                "status": status
            })

        # 3. Gaspillage Équipement (from Efficacite)
        gaspillage_equip = self.efficacite_analyzer.detecter_gaspillage()
        for gaspil in gaspillage_equip: # Corrected variable name
            alert_type = "Gaspillage Équipement"
            status = "Actif"
            description = f"Gaspillage détecté sur {gaspil['nom_equipement']} ({gaspil['nom_batiment']}): " \
                          f"Écart {gaspil['pourcentage_ecart']:.2f}% (réel vs théorique)"
            # No specific date for this type of alert, use current or most recent consumption date
            alert_date = datetime.now() 
            
            all_alerts.append({
                "date": alert_date,
                "type": alert_type,
                "source": "N/A",
                "equip_bat": gaspil["nom_equipement"],
                "description": description,
                "status": status
            })
            
        # 4. Consommation élevée pendant les heures de coupure (New analysis to be implemented)
        # Placeholder for now, will add when analysis is ready
        # conso_pdt_coupure_alerts = self.efficacite_analyzer.analyze_conso_during_coupure()
        # for cpc_alert in conso_pdt_coupure_alerts:
        #     ...

        # Apply filters
        filtered_alerts = []
        for alert in all_alerts:
            match = True
            
            # Filter by Date
            if date_debut_str:
                try:
                    date_debut_dt = datetime.fromisoformat(date_debut_str)
                    if alert["date"] < date_debut_dt:
                        match = False
                except ValueError: pass
            
            if date_fin_str:
                try:
                    date_fin_dt = datetime.fromisoformat(date_fin_str)
                    if alert["date"] > date_fin_dt:
                        match = False
                except ValueError: pass

            # Filter by Type
            if selected_alert_type is not None and alert["type"] != selected_alert_type:
                match = False

            # Filter by Status
            if selected_status is not None and alert["status"] != selected_status:
                match = False
            
            if match:
                filtered_alerts.append(alert)

        # Sort alerts by date, most recent first
        filtered_alerts.sort(key=lambda x: x["date"], reverse=True)

        # Populate table
        self.table_widget.setRowCount(len(filtered_alerts))
        for row, alert in enumerate(filtered_alerts):
            self.table_widget.setItem(row, 0, QTableWidgetItem(alert["date"].strftime("%Y-%m-%d %H:%M")))
            self.table_widget.setItem(row, 1, QTableWidgetItem(alert["type"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(alert["source"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(alert["equip_bat"]))
            self.table_widget.setItem(row, 4, QTableWidgetItem(alert["description"]))
            status_item = QTableWidgetItem(alert["status"])
            if alert["status"] == "Actif":
                status_item.setForeground(QColor("red"))
            self.table_widget.setItem(row, 5, status_item)

if __name__ == '__main__':
    import sys
    import os
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    sys.path.insert(0, project_root)

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    view = AlertesView()
    view.exec()
    sys.exit(app.exec())