from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem)
from approbot.server_gets import RequetesServeur
import threading


class OngletArbitre(QWidget):

    def __init__(self, connexion):
        super().__init__()

        self.connexion = connexion
        self.requetes = RequetesServeur()
        self.rid = None

        layout = QVBoxLayout()

        self.label_statut = QLabel("Serveur : non connecté")
        layout.addWidget(self.label_statut)

        ligne_ip = QHBoxLayout()

        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText("IP serveur ex : 192.168.1.10")

        self.bouton_connexion = QPushButton("Connexion manuelle")
        self.bouton_connexion.clicked.connect(self.connecter_ip_manuelle)

        ligne_ip.addWidget(self.input_ip)
        ligne_ip.addWidget(self.bouton_connexion)

        layout.addLayout(ligne_ip)

        self.input_reseau = QLineEdit("192.168.1")
        self.input_reseau.setPlaceholderText("Réseau ex : 192.168.1")
        layout.addWidget(self.input_reseau)

        self.bouton_recherche = QPushButton("Rechercher les serveurs")
        self.bouton_recherche.clicked.connect(self.rechercher_serveurs)
        layout.addWidget(self.bouton_recherche)

        self.liste_serveurs = QListWidget()
        layout.addWidget(self.liste_serveurs)

        self.bouton_selection = QPushButton("Se connecter au serveur sélectionné")
        self.bouton_selection.clicked.connect(self.connecter_selection)
        layout.addWidget(self.bouton_selection)

        layout.addWidget(QLabel("Nom du robot"))

        self.input_nom_robot = QLineEdit()
        self.input_nom_robot.setPlaceholderText("Nom du robot")
        layout.addWidget(self.input_nom_robot)

        self.btn_nom_robot = QPushButton("Enregistrer le robot")
        self.btn_nom_robot.clicked.connect(self.enregistrer_robot)
        layout.addWidget(self.btn_nom_robot)

        self.setLayout(layout)

    def connecter_ip_manuelle(self):
        ip = self.input_ip.text().strip()
        if not ip:
            self.label_statut.setText("Erreur : IP invalide")
            return
        self.connecter_a_ip(ip)

    def connecter_selection(self):
        item = self.liste_serveurs.currentItem()
        if item is None:
            self.label_statut.setText("Erreur : sélectionnez un serveur.")
            return
        ip = item.data(1000)
        self.connecter_a_ip(ip)

    def connecter_a_ip(self, ip):
        try:
            self.requetes.url_serveur = f"http://{ip}:8080"
            version = self.requetes.verifier_connexion()
            reponse = self.requetes.hello()
            self.rid = reponse["rid"]
            self.label_statut.setText(f"Connecté au serveur {ip} ({version})")

        except Exception as e:
            self.label_statut.setText(f"Erreur connexion : {e}")

    def rechercher_serveurs(self):
        reseau = self.input_reseau.text().strip()
        if not reseau:
            self.label_statut.setText("Erreur : réseau invalide.")
            return
        self.liste_serveurs.clear()
        self.label_statut.setText(f"Recherche sur {reseau}....")
        serveurs = []
        lock = threading.Lock()

        def sonder(i):
            ip = f"{reseau}.{i}"
            resultat = RequetesServeur.sonder_serveur(ip)
            if resultat:
                with lock:
                    serveurs.append(resultat)

        threads = []

        for i in range(1, 255):
            t = threading.Thread(target=sonder, args=(i,), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if not serveurs:
            self.label_statut.setText("Aucun serveur trouvé.")
            return

        for serveur in serveurs:
            item = QListWidgetItem(f"{serveur['nom']} - {serveur['ip']}")
            item.setData(1000, serveur["ip"])
            self.liste_serveurs.addItem(item)

        self.label_statut.setText(f"{len(serveurs)} serveur(s) trouvé(s).")

    def enregistrer_robot(self):
        nom = self.input_nom_robot.text().strip()
        if not nom:
            self.label_statut.setText("Nom invalide")
            return
        if self.rid is None:
            self.label_statut.setText("Connectez-vous au serveur d'abord")
            return
        try:
            self.requetes.nom_robot(self.rid, nom)
            self.label_statut.setText(f"Nom '{nom}' enregistré")
        except Exception as e:
            self.label_statut.setText(f"Erreur : {e}")
