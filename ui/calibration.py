from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class OngletCalibration(QWidget):
    def __init__(self, connexion):
        super().__init__()

        self.connexion = connexion

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Calibration des couleurs"))

        self.setLayout(layout)