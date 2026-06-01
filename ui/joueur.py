from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class OngletJoueur(QWidget):
    def __init__(self, connexion):
        super().__init__()

        self.connexion = connexion

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Contrôle joueur"))

        self.setLayout(layout)