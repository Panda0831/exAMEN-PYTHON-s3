from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QComboBox, QMessageBox, QScrollArea, QWidget
from PySide6.QtCore import Qt

from model.equipement_model import EquipementModel
from model.type_equipement_model import TypeEquipementModel
from analysis.efficacite import Efficacite
from view.components.matplotlib_widget import MatplotlibWidget

class EfficaciteView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyse d'Efficacité & Gaspillage")
        self.setGeometry(100, 100, 1200, 800)

        self.equipement_model = EquipementModel()
        self.type_equipement_model = TypeEquipementModel()
        self.efficacite_analyzer = Efficacite()

        self.main_layout = QVBoxLayout(self)

        self._create_widgets()
        self._update_data()

    def _create_widgets(self):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        scroll_area.setWidget(content_widget)
        self.main_layout.addWidget(scroll_area)

        # Section 1: Top 5 Équipements Énergivores (Chart)
        self.content_layout.addWidget(QLabel("<h2>Top 5 Équipements Énergivores</h2>"))
        self.top_equip_chart = MatplotlibWidget(self)
        self.top_equip_chart.setMinimumHeight(300)
        self.content_layout.addWidget(self.top_equip_chart)

        # Section 2: Analyse d'un Équipement Spécifique
        self.content_layout.addWidget(QLabel("<h2>Analyse d'un Équipement Spécifique</h2>"))
        equip_analysis_layout = QHBoxLayout()
        self.equipement_combo = QComboBox(self)
        self.equipement_combo.addItem("Sélectionnez un équipement", None)
        self._load_equipements_to_combo()
        self.equipement_combo.currentIndexChanged.connect(self._update_equipement_analysis)
        equip_analysis_layout.addWidget(self.equipement_combo)
        equip_analysis_layout.addStretch()
        self.content_layout.addLayout(equip_analysis_layout)

        self.efficacite_equip_label = QLabel("Consommation réelle vs théorique: N/A")
        self.kwh_par_heure_label = QLabel("kWh par heure d'utilisation: N/A")
        self.content_layout.addWidget(self.efficacite_equip_label)
        self.content_layout.addWidget(self.kwh_par_heure_label)

        # Section 3: Détection de Gaspillage (Table)
        self.content_layout.addWidget(QLabel("<h2>Détection de Gaspillage</h2>"))
        self.gaspillage_table = QTableWidget(self)
        self.gaspillage_table.setColumnCount(4)
        self.gaspillage_table.setHorizontalHeaderLabels(["Équipement", "Réel (kWh)", "Théorique Estimé (kWh)", "Écart (%)"])
        self.gaspillage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.gaspillage_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_layout.addWidget(self.gaspillage_table)

        # Section 4: Rendement par Type d'Équipement (Table)
        self.content_layout.addWidget(QLabel("<h2>Rendement par Type d'Équipement</h2>"))
        self.rendement_type_table = QTableWidget(self)
        self.rendement_type_table.setColumnCount(4)
        self.rendement_type_table.setHorizontalHeaderLabels(["Type", "Théorique (kWh/h)", "Réel Moy. (kWh/h)", "Rendement (%)"])
        self.rendement_type_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rendement_type_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_layout.addWidget(self.rendement_type_table)

    def _load_equipements_to_combo(self):
        equipements = self.equipement_model.get_all_equipements()
        for e in equipements:
            self.equipement_combo.addItem(f"{e['nom_equipement']} ({e['nom_batiment']})", e["id_equipement"])

    def _update_data(self):
        self._draw_top_equipments_chart()
        self._populate_gaspillage_table()
        self._populate_rendement_type_table()
        self._update_equipement_analysis() # Update initial selection

    def _draw_top_equipments_chart(self):
        fig = self.top_equip_chart.get_figure()
        fig.clear()
        ax = fig.add_subplot(111)

        data = self.efficacite_analyzer.get_equipements_plus_energivores(top_n=5)
        
        if not data:
            ax.text(0.5, 0.5, "Aucune donnée d'équipements\nénergivores à afficher", ha='center', va='center', transform=ax.transAxes)
        else:
            labels = [item['nom_equipement'] for item in data]
            kwh_values = [item['total_kwh'] for item in data]
            
            y_pos = range(len(labels))
            ax.barh(y_pos, kwh_values, align='center', color='teal')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels, fontsize=9)
            ax.invert_yaxis()
            ax.set_xlabel('Consommation Totale (kWh)', fontsize=10)
            ax.tick_params(axis='x', labelsize=9)
        
        ax.set_title("Top 5 Équipements Énergivores", fontsize=12)
        fig.tight_layout()
        self.top_equip_chart.canvas.draw_idle()

    def _update_equipement_analysis(self):
        id_equipement = self.equipement_combo.currentData()
        if id_equipement is None:
            self.efficacite_equip_label.setText("Consommation réelle vs théorique: N/A")
            self.kwh_par_heure_label.setText("kWh par heure d'utilisation: N/A")
            return
        
        # Calculer efficacité équipement
        efficacite_data = self.efficacite_analyzer.calculer_efficacite_equipement(id_equipement)
        if efficacite_data:
            self.efficacite_equip_label.setText(
                f"Consommation réelle vs théorique: Réel {efficacite_data['conso_reelle_totale']:.2f} kWh, "
                f"Théorique Estimé {efficacite_data['conso_theorique_estimee']:.2f} kWh, "
                f"Écart: {efficacite_data['ecart_kwh']:.2f} kWh ({efficacite_data['pourcentage_ecart']:.2f}%)"
            )
            # kWh par heure d'utilisation
            kwh_per_hour = self.efficacite_analyzer.calculer_kwh_par_heure_utilisation(id_equipement)
            self.kwh_par_heure_label.setText(f"kWh par heure d'utilisation: {kwh_per_hour:.2f} kWh/h")
        else:
            self.efficacite_equip_label.setText("Consommation réelle vs théorique: N/A")
            self.kwh_par_heure_label.setText("kWh par heure d'utilisation: N/A")

    def _populate_gaspillage_table(self):
        self.gaspillage_table.setRowCount(0)
        gaspillage_data = self.efficacite_analyzer.detecter_gaspillage()
        self.gaspillage_table.setRowCount(len(gaspillage_data))
        for row, item in enumerate(gaspillage_data):
            self.gaspillage_table.setItem(row, 0, QTableWidgetItem(item["nom_equipement"]))
            self.gaspillage_table.setItem(row, 1, QTableWidgetItem(f"{item['conso_reelle_totale']:.2f}"))
            self.gaspillage_table.setItem(row, 2, QTableWidgetItem(f"{item['conso_theorique_estimee']:.2f}"))
            self.gaspillage_table.setItem(row, 3, QTableWidgetItem(f"{item['pourcentage_ecart']:.2f}%"))

    def _populate_rendement_type_table(self):
        self.rendement_type_table.setRowCount(0)
        all_types = self.type_equipement_model.get_all_types_equipement()
        
        # Calculate rendement for each type
        rendement_data = []
        for type_equip in all_types:
            rendement_info = self.efficacite_analyzer.calculer_rendement_par_type_equipement(type_equip["id_type"])
            if rendement_info:
                rendement_data.append(rendement_info)

        self.rendement_type_table.setRowCount(len(rendement_data))
        for row, item in enumerate(rendement_data):
            self.rendement_type_table.setItem(row, 0, QTableWidgetItem(item["nom_type"]))
            self.rendement_type_table.setItem(row, 1, QTableWidgetItem(f"{item['conso_theorique_type']:.2f}"))
            self.rendement_type_table.setItem(row, 2, QTableWidgetItem(f"{item['conso_reelle_moyenne_par_heure']:.2f}"))
            self.rendement_type_table.setItem(row, 3, QTableWidgetItem(f"{item['pourcentage_rendement']:.2f}%"))


if __name__ == '__main__':
    import sys
    import os
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    sys.path.insert(0, project_root)

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    view = EfficaciteView()
    view.exec()
    sys.exit(app.exec())
