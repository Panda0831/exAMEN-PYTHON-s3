from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea
from PySide6.QtCore import Qt

from view.components.matplotlib_widget import MatplotlibWidget
from analysis.couts import Couts

class CoutsView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyse des Coûts Énergétiques")
        self.setGeometry(100, 100, 1000, 700)

        self.couts_analyzer = Couts()

        self.main_layout = QVBoxLayout(self)

        self._create_widgets()
        self._update_data()

    def _create_widgets(self):
        # Create a scroll area for content if it gets too long
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        scroll_area.setWidget(content_widget)
        self.main_layout.addWidget(scroll_area)

        # 1. Comparison Cards
        self.comparison_layout = QHBoxLayout()
        self.total_jirama_label = QLabel("Coût Total JIRAMA: N/A")
        self.total_groupe_label = QLabel("Coût Total Groupe Électrogène: N/A")
        self.difference_label = QLabel("Différence: N/A")
        self.comparison_layout.addWidget(self.total_jirama_label)
        self.comparison_layout.addWidget(self.total_groupe_label)
        self.comparison_layout.addWidget(self.difference_label)
        self.content_layout.addLayout(self.comparison_layout)

        # 2. Cost Comparison Graph
        self.cost_comparison_chart = MatplotlibWidget(self)
        self.cost_comparison_chart.setMinimumHeight(300)
        self.content_layout.addWidget(self.cost_comparison_chart)

        # 3. Cost by Period Graph (e.g., Daily Cost)
        self.cost_by_period_chart = MatplotlibWidget(self)
        self.cost_by_period_chart.setMinimumHeight(350)
        self.content_layout.addWidget(self.cost_by_period_chart)

        # 4. Optional: Surcoût Coupures
        self.surcout_coupures_label = QLabel("Surcoût Coupures: N/A")
        self.content_layout.addWidget(self.surcout_coupures_label)

    def _update_data(self):
        # Update Comparison Cards
        comparaison_data = self.couts_analyzer.comparer_couts_sources()
        if comparaison_data:
            self.total_jirama_label.setText(f"Coût Total JIRAMA: {comparaison_data['JIRAMA']:.2f} Ariary")
            self.total_groupe_label.setText(f"Coût Total Groupe Électrogène: {comparaison_data['Groupe électrogène']:.2f} Ariary")
            self.difference_label.setText(f"Différence (Groupe - JIRAMA): {comparaison_data['difference']:.2f} Ariary")
        else:
            self.total_jirama_label.setText("Coût Total JIRAMA: N/A")
            self.total_groupe_label.setText("Coût Total Groupe Électrogène: N/A")
            self.difference_label.setText("Différence: N/A")

        # Draw Cost Comparison Graph
        self._draw_cost_comparison_chart(comparaison_data)

        # Draw Cost by Period Graph
        couts_par_jour_data = self.couts_analyzer.calculer_cout_par_periode(periode='jour')
        self._draw_cost_by_period_chart(couts_par_jour_data)

        # Update Surcoût Coupures
        surcout_coupures = self.couts_analyzer.calculer_surcout_coupures()
        self.surcout_coupures_label.setText(f"Surcoût Coupures (estimation): {surcout_coupures:.2f} Ariary")

    def _draw_cost_comparison_chart(self, comparaison_data):
        fig = self.cost_comparison_chart.get_figure()
        fig.clear()
        ax = fig.add_subplot(111)

        if not comparaison_data:
            ax.text(0.5, 0.5, "Aucune donnée de coûts\nà comparer", ha='center', va='center', transform=ax.transAxes)
        else:
            sources = [key for key in comparaison_data.keys() if key != "difference"]
            couts = [comparaison_data[key] for key in sources]
            
            colors = ['#4A90E2', '#D0021B']
            bars = ax.bar(sources, couts, color=colors)
            ax.set_ylabel("Coût Total (Ariary)")
            ax.set_title("Comparaison des Coûts Totaux par Source")
            ax.tick_params(axis='x', labelsize=10)
            ax.tick_params(axis='y', labelsize=10)
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:,.2f} Ariary', va='bottom', ha='center', fontsize=9)
        
        fig.tight_layout()
        self.cost_comparison_chart.canvas.draw_idle()

    def _draw_cost_by_period_chart(self, couts_par_jour_data):
        fig = self.cost_by_period_chart.get_figure()
        fig.clear()
        ax = fig.add_subplot(111)

        if not couts_par_jour_data:
            ax.text(0.5, 0.5, "Aucune donnée de coûts\npar période", ha='center', va='center', transform=ax.transAxes)
        else:
            jours = list(couts_par_jour_data.keys())
            couts = list(couts_par_jour_data.values())

            ax.bar(jours, couts, color='lightgray')
            ax.set_xlabel("Jour")
            ax.set_ylabel("Coût Total (Ariary)")
            ax.set_title("Coût de la Consommation Énergétique par Jour")
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        fig.tight_layout()
        self.cost_by_period_chart.canvas.draw_idle()

if __name__ == '__main__':
    import sys
    import os
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    sys.path.insert(0, project_root)

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    view = CoutsView()
    view.exec()
    sys.exit(app.exec())
