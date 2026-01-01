from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor

from model.coupure_model import CoupureModel
from analysis.statistiques import Statistique
from datetime import datetime
from config.colors import AppColors # Import AppColors

class AlertsTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)
        
        self.coupure_model = CoupureModel()
        self.statistique_analyzer = Statistique()
        
        self.setup_table()
        self.populate_data()

    def setup_table(self):
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Date", "Type", "Description"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers) # Make table read-only

    def populate_data(self):
        # Fetch data
        coupures = self.coupure_model.get_all_coupures()
        anomalies = self.statistique_analyzer.anomalies()
        
        # Combine and sort events
        events = []
        for coupure in coupures:
            events.append({
                "date": datetime.fromisoformat(coupure["debut_coupure"]),
                "type": "Coupure",
                "description": f"Coupure à {coupure['nom_batiment']}. Fin: {coupure['fin_coupure'] or 'En cours'}. Cause: {coupure['cause'] or 'N/A'}",
                "severity": "high"
            })
            
        for anomalie in anomalies:
            events.append({
                "date": datetime.fromisoformat(anomalie["date_heure"]),
                "type": "Anomalie",
                "description": f"Pic de consommation sur {anomalie['nom_equipement']}: {anomalie['energie_kwh']:.2f} kWh",
                "severity": "medium"
            })

        # Sort events by date, most recent first
        events.sort(key=lambda x: x["date"], reverse=True)
        
        # Populate table
        self.table_widget.setRowCount(len(events))
        for row, event in enumerate(events):
            date_item = QTableWidgetItem(event["date"].strftime("%Y-%m-%d %H:%M"))
            type_item = QTableWidgetItem(event["type"])
            desc_item = QTableWidgetItem(event["description"])
            
            # Color coding for severity
            if event["severity"] == "high":
                type_item.setBackground(QColor(AppColors.Danger)) # Use AppColors
                type_item.setForeground(QColor(AppColors.White)) # Use AppColors
            elif event["severity"] == "medium":
                type_item.setBackground(QColor(AppColors.Warning)) # Use AppColors

            self.table_widget.setItem(row, 0, date_item)
            self.table_widget.setItem(row, 1, type_item)
            self.table_widget.setItem(row, 2, desc_item)
