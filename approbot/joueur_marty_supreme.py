import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("marty.supreme.app")

from PyQt6.QtGui import QIcon,QFont
chemin_icone = os.path.join(base_dir, "ui", "assets", "logo.ico")

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTabWidget
)
#BACK-END IMPORTS#
from approbot.calibrateur_couleurs import CalibrateurCouleurs
from approbot.connexion_marty import ConnexionMarty

#FRONT-END IMPORTS#
from ui.connexion import OngletConnexion
from ui.calibration import OngletCalibration
from ui.joueur import OngletJoueur
from ui.arbitre import OngletArbitre


class MartySupreme(QWidget):
    def __init__(self):
        super().__init__()

        self.connexion = ConnexionMarty()
        self.calibration = CalibrateurCouleurs(self.connexion)

        self.setWindowTitle("Marty Supreme")
        self.setWindowIcon(QIcon(chemin_icone))
        self.resize(900, 600)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tabs.addTab(
            OngletConnexion(self.connexion),
            "Connexion"
        )

        self.tabs.addTab(
            OngletCalibration(self.connexion),
            "Calibration"
        )

        self.tabs.addTab(
            OngletJoueur(self.connexion, self.calibration),
            "Joueur"
        )

        self.tabs.addTab(
            OngletArbitre(self.connexion),
            "Arbitre"
        )

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def closeEvent(self, event):
        self.connexion.deconnecter()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(chemin_icone))

    app.setFont(QFont("Segoe UI", 10))

    app.setStyleSheet("""
        QWidget {
            background-color: #1e1e2f;
            color: #f5f5f5;
        }

        QTabWidget::pane {
            border: 1px solid #444;
            border-radius: 8px;
            padding: 6px;
        }

        QTabBar::tab {
            background: #2b2b40;
            color: #dddddd;
            padding: 10px 18px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 3px;
        }

        QTabBar::tab:selected {
            background: #4b6cff;
            color: white;
        }

        QGroupBox {
            border: 1px solid #5d5d7a;
            border-radius: 10px;
            margin-top: 12px;
            padding: 12px;
            font-weight: bold;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }

        QPushButton {
            background-color: #4b6cff;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 9px;
        }

        QPushButton:hover {
            background-color: #6f86ff;
        }

        QPushButton:pressed {
            background-color: #324bd6;
        }

        QLineEdit {
            background-color: #2b2b40;
            color: white;
            border: 1px solid #5d5d7a;
            border-radius: 8px;
            padding: 8px;
        }

        QListWidget {
            background-color: #2b2b40;
            border: 1px solid #5d5d7a;
            border-radius: 8px;
            padding: 6px;
        }

        QListWidget::item {
            padding: 8px;
        }

        QListWidget::item:selected {
            background-color: #4b6cff;
        }
        """)

    window = MartySupreme()
    window.show()

    sys.exit(app.exec())