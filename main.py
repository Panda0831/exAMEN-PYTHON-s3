import sys
import os
from PySide6.QtWidgets import QApplication # Import QApplication to apply stylesheet

from controller.main_controller import MainController

if __name__ == '__main__':
    # Initialize QApplication first to load stylesheet
    app = QApplication(sys.argv)

    # Load and apply stylesheet
    qss_path = os.path.join(os.path.dirname(__file__), 'config', 'style.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Stylesheet not found at {qss_path}")

    controller = MainController(app) # Pass the QApplication instance to the controller
    controller.run()
