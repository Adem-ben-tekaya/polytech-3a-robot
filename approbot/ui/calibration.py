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

        self.bouton_mesure = QPushButton("Enregistrer une mesure")
        self.bouton_mesure.clicked.connect(self.enregistrer_mesure)

        self.bouton_suivant = QPushButton("Couleur suivante")
        self.bouton_suivant.clicked.connect(self.couleur_suivante)

        self.bouton_sauvegarder = QPushButton("Sauvegarder calibration")
        self.bouton_sauvegarder.clicked.connect(self.sauvegarder)

        layout.addWidget(self.bouton_mesure)
        layout.addWidget(self.bouton_suivant)
        layout.addWidget(self.bouton_sauvegarder)

        self.liste_mesures = QListWidget()
        layout.addWidget(self.liste_mesures)

        self.setLayout(layout)

    def enregistrer_mesure(self):
        nom = self.champ_nom.text()
        condition = self.combobox_condition.currentText()

        if nom == "":
            self.liste_mesures.addItem("Erreur : entre un nom de couleur")
            return

        # À adapter selon ta classe connexion
        valeur_hex = self.calibrateur.lire_hex_capteur()

        self.calibrateur.enregistrer_mesure(
            nom_couleur=nom,
            condition=condition,
            valeur_hex=valeur_hex
        )

        self.liste_mesures.addItem(
            f"Couleur #{self.calibrateur.numero_couleur} | {nom} | {condition} | #{valeur_hex}"
        )

    def couleur_suivante(self):
        self.calibrateur.couleur_suivante()
        self.liste_mesures.addItem("---- Couleur suivante ----")

    def sauvegarder(self):
        nom_fichier = self.calibrateur.sauvegarder()
        self.liste_mesures.addItem(f"Calibration sauvegardée dans : {nom_fichier}")