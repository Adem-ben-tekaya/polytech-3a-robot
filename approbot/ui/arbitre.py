from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class OngletArbitre(QWidget):
    def __init__(self, connexion):
        super().__init__()

        self.connexion = connexion

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Interface arbitre"))

        self.setLayout(layout)