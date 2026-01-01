from PySide6.QtWidgets import QWidget, QVBoxLayout
from view.components.matplotlib_widget import MatplotlibWidget
from model.consommation_model import ConsommationModel
from datetime import datetime

class MainChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.matplotlib_widget = MatplotlibWidget(self)
        self.layout.addWidget(self.matplotlib_widget)
        self.consommation_model = ConsommationModel()
        self.draw_chart(building_id=None)

    def draw_chart(self, building_id=None):
        self.matplotlib_widget.clear_figure()
        fig = self.matplotlib_widget.get_figure()
        ax = fig.add_subplot(111)
        
        # Get all consumption data (for simplicity, we'll plot all of it,
        # but for "24h" we'd filter by a time range)
        if building_id:
            all_consos = self.consommation_model.get_consommation_by_building(building_id)
        else:
            all_consos = self.consommation_model.get_all_consommation()
        
        if not all_consos:
            ax.text(0.5, 0.5, "Aucune donnée de consommation", horizontalalignment='center',
                    verticalalignment='center', transform=ax.transAxes)
            ax.set_title("Courbe de Consommation 24h")
            self.matplotlib_widget.canvas.draw_idle()
            return
            
        # Filter for the last 24 hours if needed, but for now, plot all
        # Assuming date_heure is in ISO format
        all_consos.sort(key=lambda x: datetime.fromisoformat(x['date_heure']))

        dates = [datetime.fromisoformat(item['date_heure']) for item in all_consos]
        energies = [item['energie_kwh'] for item in all_consos]

        ax.plot(dates, energies, marker='o', linestyle='-')
        ax.set_xlabel("Heure")
        ax.set_ylabel("Consommation (kWh)")
        ax.set_title("Courbe de Consommation (Historique)") # Changed from 24h for now
        ax.grid(True)
        fig.autofmt_xdate() # Format dates nicely

        self.matplotlib_widget.canvas.draw_idle()
