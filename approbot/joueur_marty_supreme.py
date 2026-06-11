import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("marty.supreme.app")

from PyQt6.QtGui import QIcon,QFont
chemin_icone = os.path.join(base_dir,"approbot", "ui", "assets", "logo.ico")

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTabWidget
)
#BACK-END IMPORTS#
from approbot.calibrateur_couleurs import CalibrateurCouleurs
from approbot.connexion_marty import ConnexionMarty
from approbot.server_gets import ServerGets

#FRONT-END IMPORTS#
from ui.connexion import OngletConnexion
from ui.calibration import OngletCalibration
from ui.joueur import OngletJoueur
from ui.arbitre import OngletArbitre
from ui.style import STYLE


class MartySupreme(QWidget):
    def __init__(self):
        super().__init__()

        self.connexion = ConnexionMarty()
        self.serveur = ServerGets()
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
            OngletJoueur(self.connexion, self.calibration, self.serveur),
            "Joueur"
        )

        self.tabs.addTab(
            OngletArbitre(self.connexion, self.serveur),
            "Arbitre"
        )

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def closeEvent(self, event):
        print("Fermeture de l'app")
        print("Serveur URL :", self.serveur.url_serveur)
        print("Serveur RID :", self.serveur.rid)

        try:
            self.connexion.deconnecter()
            print("Marty déconnecté")
        except Exception as e:
            print("Erreur déconnexion Marty :", e)

        try:
            self.serveur.deconnecter()
            print("Serveur déconnecté")
        except Exception as e:
            print("Erreur déconnexion serveur :", e)

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(chemin_icone))

    app.setFont(QFont("Segoe UI", 10))

    app.setStyleSheet(STYLE)

    window = MartySupreme()
    window.show()

    sys.exit(app.exec())