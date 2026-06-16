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
from ui.dance import OngletDance
from ui.style import STYLE


class MartySupreme(QWidget):
    def __init__(self):
        super().__init__()

        self.connexion = ConnexionMarty()
        self.serveur = ServerGets()
        self.calibration = CalibrateurCouleurs(self.connexion)
        self.onglet_dance = OngletDance(self.connexion, self.calibration, self.serveur)

        self.setWindowTitle("Marty Supreme")
        self.setWindowIcon(QIcon(chemin_icone)) #Définir une icône personalisée
        self.resize(900, 600)

        layout = QVBoxLayout()

        self.tabs = QTabWidget() #Afin d'avoir une application facile a prendre en main on utilise des onglets de PyQt

        self.tabs.addTab(
            OngletConnexion(self.connexion),
            "Connexion"
        )

        self.tabs.addTab(
            OngletCalibration(self.connexion, self.calibration),
            "Calibration"
        )

        self.tabs.addTab(
            OngletJoueur(self.connexion, self.calibration, self.serveur),
            "Joueur"
        )

        self.tabs.addTab(self.onglet_dance, "Chorégraphie")

        self.tabs.addTab(
            OngletArbitre(self.connexion, self.serveur),
            "Arbitre"
        )

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def closeEvent(self, event):
        """
        Gestion des arrets innnatendus pour éviter de 
        conserver une connexion avec marty ou avec le 
        serveur et de garder la dance en mémoire apres 
        la fermeture de l'appli.
        """
        try:
            self.onglet_dance.cleanup()
        except Exception:
            pass

        try:
            self.connexion.deconnecter()
        except Exception:
            pass

        try:
            self.serveur.deconnecter()
        except Exception:
            pass

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setFont(QFont("Segoe UI", 10))

    app.setStyleSheet(STYLE) #Définir un style QSS

    window = MartySupreme()
    window.showMaximized()

    sys.exit(app.exec())