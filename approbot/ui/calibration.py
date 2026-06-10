from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QComboBox
)

from approbot.calibrateur_couleurs import CalibrateurCouleurs

class OngletCalibration(QWidget):
    def __init__(self, connexion):
        super().__init__()

        self.connexion = connexion
        self.calibrateur = CalibrateurCouleurs(self.connexion)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Calibration des couleurs"))

        self.champ_nom = QLineEdit()
        self.champ_nom.setPlaceholderText("Nom de la couleur : rouge, bleu, noir...")

        self.combobox_condition = QComboBox()
        self.combobox_condition.addItems([
            "Très lumineux",
            "Normal",
            "Très sombre"
        ])

        layout.addWidget(self.champ_nom)
        layout.addWidget(self.combobox_condition)

        self.bouton_mesure = QPushButton("Enregistrer la mesure")
        self.bouton_mesure.clicked.connect(self.ajouter_mesure)

        layout.addWidget(self.bouton_mesure)

        self.liste_mesures = QListWidget()
        layout.addWidget(self.liste_mesures)

        self.setLayout(layout)

    def ajouter_mesure(self):
        couleur = self.champ_nom.text()
        condition = self.combobox_condition.currentText()

        if couleur == "":
            self.liste_mesures.addItem("Erreur : entre un nom de couleur")
            return

        self.calibrateur.ajouter_mesure(
            couleur_reelle=couleur,
            eclairage=condition
        )