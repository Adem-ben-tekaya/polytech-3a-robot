import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel,    
    QPushButton, 
    QTableWidget, 
    QTableWidgetItem, 
    QTextEdit,
    QFileDialog, 
    QHeaderView, 
    QFrame, 
    QSplitter, 
    QStatusBar, 
    QLineEdit
    )

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextCursor
from gestion_battle import (
    robots_connus, 
    charger_battle, 
    charger_classement
)

from signaux import signals
from api_rest import FlaskThread
from ui.style import COLOR_MAP
import socket
import ctypes


class FenetrePrincipale(QMainWindow):

    def __init__(self):
        super().__init__()
        self.flask_thread: FlaskThread | None = None
        self.battle_charge = False
        self.port_actuel = 8080
        self.setWindowTitle("Dance Battle — Serveur Arbitre")
        self.setMinimumSize(1000, 680)
        self.construire_ui()
        self.connecter_signaux()
        self.rafraichir_tables()

    def construire_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 8)
        root.setSpacing(8)

        #En-tête
        entete = QHBoxLayout()
        gauche = QVBoxLayout()
        t = QLabel("DANCE BATTLE")
        t.setObjectName("titre")
        s = QLabel("SERVEUR - ARBITRE")
        s.setObjectName("sous_titre")
        gauche.addWidget(t)
        gauche.addWidget(s)
        entete.addLayout(gauche)
        entete.addStretch()

        #Contrôles serveur
        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)

        lbl_port = QLabel("PORT")
        lbl_port.setObjectName("section")
        self.spin_port = QLineEdit("8080")
        self.spin_port.setFixedWidth(80)

        self.btn_battle = QPushButton("📂  CHARGER .battle")
        self.btn_start = QPushButton("▶  DÉMARRER")
        self.btn_stop = QPushButton("■  ARRÊTER")
        self.btn_start.setObjectName("btn_start")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setEnabled(False)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)
        connexion_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connexion_temp.connect(("8.8.8.8", 80))
        mon_ip = connexion_temp.getsockname()[0]
        connexion_temp.close()
        lbl_ip = QLabel(f"IP : {mon_ip}")
        lbl_ip.setObjectName("section")
        ctrl.addWidget(lbl_ip)
        ctrl.addSpacing(16)

        ctrl.addWidget(lbl_port)
        ctrl.addWidget(self.spin_port)
        ctrl.addSpacing(8)
        ctrl.addWidget(self.btn_battle)
        ctrl.addWidget(self.btn_start)
        ctrl.addWidget(self.btn_stop)
        entete.addLayout(ctrl)
        root.addLayout(entete)

        #Séparateur
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        #Corps principal
        splitter = QSplitter(Qt.Orientation.Horizontal)

        #Panneau gauche : robots + classement
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(6)

        lbl_robots = QLabel("ROBOTS CONNECTÉS")
        lbl_robots.setObjectName("section")
        left_layout.addWidget(lbl_robots)

        self.table_robots = QTableWidget(0, 3)
        self.table_robots.setHorizontalHeaderLabels(["ID", "NOM", "SCORE"])
        self.table_robots.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_robots.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_robots.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table_robots.setColumnWidth(0, 90)
        self.table_robots.setColumnWidth(2, 70)
        self.table_robots.verticalHeader().setVisible(False)
        self.table_robots.setAlternatingRowColors(True)
        self.table_robots.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_robots.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        left_layout.addWidget(self.table_robots)

        lbl_class = QLabel("CLASSEMENT")
        lbl_class.setObjectName("section")
        left_layout.addWidget(lbl_class)

        self.table_class = QTableWidget(0, 3)
        self.table_class.setHorizontalHeaderLabels(["#", "NOM", "SCORE"])
        self.table_class.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_class.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_class.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table_class.setColumnWidth(0, 30)
        self.table_class.setColumnWidth(2, 70)
        self.table_class.verticalHeader().setVisible(False)
        self.table_class.setAlternatingRowColors(True)
        self.table_class.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.table_class)

        splitter.addWidget(left_panel)

        #Panneau droit : log en direct
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(6)

        lbl_log = QLabel("RÉCEPTIONS EN DIRECT")
        lbl_log.setObjectName("section")
        right_layout.addWidget(lbl_log)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        right_layout.addWidget(self.log)

        btn_effacer = QPushButton("EFFACER LOG")
        btn_effacer.clicked.connect(self.log.clear)
        right_layout.addWidget(btn_effacer)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 580])

        root.addWidget(splitter, 1)

        #Barre de statut
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.lbl_status = QLabel("🔴 Serveur arrêté  -  Aucun fichier .battle chargé")
        self.status.addWidget(self.lbl_status)
        self.lbl_battle_info = QLabel("")
        self.status.addPermanentWidget(self.lbl_battle_info)

    def connecter_signaux(self):
        self.btn_start.clicked.connect(self.demarrer_serveur)
        self.btn_stop.clicked.connect(self.arreter_serveur)
        self.btn_battle.clicked.connect(self.charger_battle)
        signals.robot_enregistre.connect(self.robot_enregistre)
        signals.robot_deconnecte.connect(self.robot_deconnecte)
        signals.pas_recu.connect(self.pas_recu)
        signals.score_mis_a_jour.connect(self.rafraichir_tables)
        signals.serveur_demarre.connect(self.serveur_demarre)
        signals.serveur_arrete.connect(self.serveur_arrete)


    def lancer_firewall_helper(self, action: str, port: int) -> bool:
        """
        Lance Marty Supreme Firewall.exe en administrateur.

        action : "add" ou "delete"
        port   : port du serveur Flask, ex 8080
        """
        racine_projet = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )

        chemin_helper = os.path.join(
            racine_projet,
            "dist",
            "AppServer-Firewall.exe"
        )

        if not os.path.exists(chemin_helper):
            self._log(f"Helper pare-feu introuvable : {chemin_helper}", "#e74c3c")
            print("To compile helper you must run :")
            print(r'.\.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --uac-admin --icon="appserver\ui\assets\logo.ico" --name "AppServer-Firewall" firewall_helper.py')
            return False

        resultat = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            chemin_helper,
            f"{action} {port}",
            None,
            0
        )

        return resultat > 32

    def demarrer_serveur(self):
        try:
            self.port_actuel = int(self.spin_port.text())
        except ValueError:
            self._log("Port invalide.", "#e74c3c")
            return

        ok = self.lancer_firewall_helper("add", self.port_actuel)

        if not ok:
            self._log("Autorisation pare-feu refusée ou impossible.", "#e74c3c")
            return

        self._log("Règle pare-feu temporaire ajoutée.", "#2ecc71")

        self.flask_thread = FlaskThread(self.port_actuel)
        self.flask_thread.start()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.spin_port.setEnabled(False)

    def arreter_serveur(self):
        if self.flask_thread:
            self.flask_thread.stop()
            self.flask_thread.wait(3000)
            self.flask_thread = None

        ok = self.lancer_firewall_helper("delete", self.port_actuel)

        if ok:
            self._log("Règle pare-feu supprimée", "#2ecc71")
        else:
            self._log("Suppression pare-feu refusée ou impossible.", "#e74c3c")

        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.spin_port.setEnabled(True)
        self.maj_status()

    def charger_battle(self):
        chemin, _ = QFileDialog.getOpenFileName(self, "Charger un fichier .battle", "", "Battle files (*.battle);;All files (*)")
        if not chemin:
            return
        charger_battle(chemin)
        self.battle_charge = True
        nom = chemin.split('/')[-1].split('\\')[-1]
        self.lbl_battle_info.setText(f"{nom}")
        self._log(f"Fichier chargé : {nom}", "#f39c12")
        self.maj_status()

    def robot_enregistre(self, rid: str):
        self._log(f"Nouveau robot connecté : {rid}", "#2ecc71")
        self.rafraichir_tables()

    def robot_deconnecte(self, rid: str):
        self._log(f"Robot déconnecté : {rid}", "#e74c3c")
        self.rafraichir_tables()

    def pas_recu(self, rid: str, col: str, arm: str, exp: str, points: int):
        couleur_hex, couleur_nom = COLOR_MAP.get(col, ('#888', col))
        signe = "+" if points >= 0 else ""
        pts_str = f"{signe}{points} pt{'s' if abs(points) != 1 else ''}"
        couleur_pts = "#2ecc71" if points > 0 else ("#e74c3c" if points < 0 else "#888")
        heure = datetime.now().strftime("%H:%M:%S")
        self.log.moveCursor(QTextCursor.MoveOperation.End)
        html = (f'<span style="color:#555a72">{heure}</span> '
                f'<span style="color:#9aa0bf">[{rid}]</span> '
                f'<span style="background:{couleur_hex};color:#fff;padding:0 4px;border-radius:2px">&nbsp;{couleur_nom}&nbsp;</span> '
                f'<span style="color:#c8ccd8">bras=<b>{arm}</b> exp=<b>{exp}</b></span> '
                f'<span style="color:{couleur_pts};font-weight:bold"> {pts_str}</span><br>')
        self.log.insertHtml(html)
        self.log.moveCursor(QTextCursor.MoveOperation.End)

    def serveur_demarre(self, port: int):
        self._log(f"Serveur démarré sur le port {port}", "#3498db")
        self.maj_status()

    def serveur_arrete(self):
        self._log("Serveur arrêté.", "#e74c3c")
        self.maj_status()

    def _log(self, texte: str, couleur: str = "#9aa0bf"):
        heure = datetime.now().strftime("%H:%M:%S")
        self.log.moveCursor(QTextCursor.MoveOperation.End)
        self.log.insertHtml(f'<span style="color:{couleur}">{texte}</span><br>')
        self.log.moveCursor(QTextCursor.MoveOperation.End)

    def rafraichir_tables(self):
        self.table_robots.setRowCount(0)
        for robot in robots_connus:
            row = self.table_robots.rowCount()
            self.table_robots.insertRow(row)
            self.table_robots.setItem(row, 0, QTableWidgetItem(robot[0]))
            self.table_robots.setItem(row, 1, QTableWidgetItem(robot[1]))
            score_item = QTableWidgetItem(str(robot[2]))
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            couleur = "#2ecc71" if robot[2] > 0 else ("#e74c3c" if robot[2] < 0 else "#9aa0bf")
            score_item.setForeground(QColor(couleur))
            self.table_robots.setItem(row, 2, score_item)

        self.table_class.setRowCount(0)
        classement = charger_classement()
        medailles = ["🥇", "🥈", "🥉"]
        for i, robot in enumerate(classement):
            row = self.table_class.rowCount()
            self.table_class.insertRow(row)
            rang = medailles[i] if i < 3 else str(i + 1)
            rang_item = QTableWidgetItem(rang)
            rang_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_class.setItem(row, 0, rang_item)
            self.table_class.setItem(row, 1, QTableWidgetItem(robot["nom"]))
            s_item = QTableWidgetItem(str(robot["score"]))
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            s_item.setForeground(QColor("#f1c40f" if i == 0 else "#9aa0bf"))
            self.table_class.setItem(row, 2, s_item)

    def maj_status(self):
        en_marche = self.flask_thread is not None and self.flask_thread.isRunning()
        srv_txt = f"🟢 Serveur actif  -  port {self.spin_port.text()}" if en_marche else "🔴 Serveur arrêté"
        battle_txt = "Fichier .battle chargé" if self.battle_charge else "Aucun fichier .battle"
        self.lbl_status.setText(f"{srv_txt}  -  {battle_txt}")

    def closeEvent(self, event):
        if self.flask_thread and self.flask_thread.isRunning():
            self.arreter_serveur()

        event.accept()