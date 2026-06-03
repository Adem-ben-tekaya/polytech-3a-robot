import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTabWidget
)
#BACK-END IMPORTS#
from Joueur.calibrateur_couleurs import CalibrateurCouleurs
from Joueur.connexion_marty import ConnexionMarty

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
            OngletJoueur(self.connexion),
            "Joueur"
        )

        self.tabs.addTab(
            OngletArbitre(self.connexion),
            "Arbitre"
        )

        layout.addWidget(self.tabs)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MartySupreme()
    window.show()

    sys.exit(app.exec())