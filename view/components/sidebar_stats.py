from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import numpy as np
from view.components.matplotlib_widget import MatplotlibWidget
from analysis.couts import Couts
from analysis.efficacite import Efficacite
from config.colors import AppColors # Import AppColors

class SidebarStats(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320) # Set a fixed width for the sidebar
        self.layout = QVBoxLayout(self)
        
        # --- Source Distribution Chart ---
        self.source_dist_chart = MatplotlibWidget(self)
        self.layout.addWidget(self.source_dist_chart)
        
        # --- Top Equipments Chart ---
        self.top_equip_chart = MatplotlibWidget(self)
        self.layout.addWidget(self.top_equip_chart)
        
        # --- Analysis instances ---
        self.couts_analyzer = Couts()
        self.efficacite_analyzer = Efficacite()

        self.draw_charts()

    def draw_charts(self):
        self.draw_source_distribution()
        self.draw_top_equipments()
    
    def draw_source_distribution(self):
        fig = self.source_dist_chart.get_figure()
        fig.clear()
        ax = fig.add_subplot(111)
        
        data = self.couts_analyzer.comparer_couts_sources()
        sources = [key for key in data.keys() if key != "difference"]
        couts = [data[key] for key in sources]

        if not sources or sum(couts) == 0:
            ax.text(0.5, 0.5, "Données de coûts\nindisponibles", ha='center', va='center', transform=ax.transAxes)
        else:
            colors = [AppColors.ChartPieJirama, AppColors.ChartPieGroupe] # Use AppColors
            ax.pie(couts, labels=sources, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        ax.set_title("Répartition des Coûts par Source")
        self.source_dist_chart.canvas.draw_idle()

    def draw_top_equipments(self):
        fig = self.top_equip_chart.get_figure()
        fig.clear()
        
        # Set a specific figure size for this chart (width, height)
        # The width will still be constrained by the QWidget layout
        # but this gives more vertical space for labels.
        fig.set_size_inches(fig.get_size_inches()[0], 4.5) # Maintain width, set height to 4.5 inches

        ax = fig.add_subplot(111)

        data = self.efficacite_analyzer.get_equipements_plus_energivores(top_n=5)
        
        if not data:
            ax.text(0.5, 0.5, "Données d'équipements\nindisponibles", ha='center', va='center', transform=ax.transAxes)
        else:
            labels = [item['nom_equipement'] for item in data]
            kwh_values = [item['total_kwh'] for item in data]
            
            y_pos = np.arange(len(labels)) # Use numpy arange for positions
            ax.barh(y_pos, kwh_values, align='center', color=AppColors.ChartBarDefault) # Use AppColors
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels, fontsize=9)
            ax.invert_yaxis()
            ax.set_xlabel('Consommation Totale (kWh)', fontsize=10)
            ax.tick_params(axis='x', labelsize=9)
        
        ax.set_title("Top 5 Équipements Énergivores", fontsize=12)
        fig.tight_layout(pad=1.0) # Add some padding
        self.top_equip_chart.canvas.draw_idle()
