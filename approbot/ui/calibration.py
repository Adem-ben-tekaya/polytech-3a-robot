from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QComboBox
)

from approbot.calibrateur_couleurs import CalibrateurCouleurs

class OngletCalibration(QWidget):
    def __init__(self, connexion, calibrateur=None):
        super().__init__()

        self.connexion = connexion
        self.calibrateur = calibrateur if calibrateur is not None else CalibrateurCouleurs(connexion)

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

        self.console = QListWidget()
        layout.addWidget(self.console)

        self.setLayout(layout)

    def ajouter_mesure(self):
        couleur = self.champ_nom.text().strip()
        condition = self.combobox_condition.currentText()

        if couleur == "":
            self.console.addItem("Erreur : entre un nom de couleur")
            return
        try:
            mesure = self.calibrateur.ajouter_mesure(
                couleur_reelle=couleur,
                eclairage=condition
            )
            self.console.addItem(
                f"✓ '{couleur}' enregistré — hex: {mesure['hex']}  ({condition})"
            )
            self.console.scrollToBottom()
            self.champ_nom.clear()

        except RuntimeError as e:
            self.console.addItem(f"Erreur : {e}")

        except Exception as e:
            self.console.addItem(f"Erreur calibration : {e}")
