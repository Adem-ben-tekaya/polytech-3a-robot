'''
Signaux PYQT
Permet la communication entre le serveur Flask et l'interface

Flask tourne dans un thread séparé pour ne pas bloquer l'interface.
Mais on ne peut pas modifier directement les widgets PyQt depuis un autre thread,
c'est dangereux et peut provoquer des crashes. Les signaux PyQt règlent ce problème :
on émet un signal depuis Flask, PyQt le reçoit et met à jour l'interface en toute sécurité.
'''

from PyQt6.QtCore import pyqtSignal, QObject

class ServerSignals(QObject):
    robot_enregistre = pyqtSignal(str)                     #id
    robot_deconnecte = pyqtSignal(str)                     #id
    pas_recu = pyqtSignal(str, str, str, str, int)         #id, col, arm, exp, points
    score_mis_a_jour = pyqtSignal()
    serveur_demarre = pyqtSignal(int)                      #port
    serveur_arrete = pyqtSignal()

signals = ServerSignals()
