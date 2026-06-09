from PyQt6.QtCore import pyqtSignal, QObject

class ServerSignals(QObject):
    robot_enregistre = pyqtSignal(str)                     # rid
    robot_deconnecte = pyqtSignal(str)                     # rid
    pas_recu = pyqtSignal(str, str, str, str, int)         # rid, col, arm, exp, points
    score_mis_a_jour = pyqtSignal()
    serveur_demarre = pyqtSignal(int)                      # port
    serveur_arrete = pyqtSignal()

signals = ServerSignals()
