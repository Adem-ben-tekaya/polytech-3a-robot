from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem
)


class OngletConnexion(QWidget):
    def __init__(self, connexion):
        super().__init__()

        self.connexion = connexion

        layout = QVBoxLayout()

        self.label_statut = QLabel("Statut : non connecté")
        layout.addWidget(self.label_statut)

        ligne_ip = QHBoxLayout()

        self.input_ip = QLineEdit("192.168.0.103")
        self.input_ip.setPlaceholderText("IP du Marty ex : 192.168.0.104")

        self.bouton_connexion = QPushButton("Connexion manuelle")
        self.bouton_connexion.clicked.connect(self.connecter_ip_manuelle)

        ligne_ip.addWidget(self.input_ip)
        ligne_ip.addWidget(self.bouton_connexion)
        layout.addLayout(ligne_ip)

        self.input_reseau = QLineEdit("192.168.0")
        self.input_reseau.setPlaceholderText("Réseau ex : 192.168.0")
        layout.addWidget(self.input_reseau)

        self.bouton_recherche = QPushButton("Rechercher les Marty")
        self.bouton_recherche.clicked.connect(self.rechercher_martys)
        layout.addWidget(self.bouton_recherche)

        self.liste_martys = QListWidget()
        layout.addWidget(self.liste_martys)

        self.bouton_selection = QPushButton("Se connecter au Marty sélectionné")
        self.bouton_selection.clicked.connect(self.connecter_selection)
        layout.addWidget(self.bouton_selection)

        self.bouton_deconnexion = QPushButton("Déconnecter")
        self.bouton_deconnexion.clicked.connect(self.deconnecter)
        layout.addWidget(self.bouton_deconnexion)

        self.setLayout(layout)

    def connecter_ip_manuelle(self):
        ip = self.connexion.nettoyer_adresse_marty(self.input_ip.text())

        if not ip:
            self.label_statut.setText("Erreur : entre une IP valide.")
            return

        self.connecter_a_ip(ip)

    def rechercher_martys(self):
        import time
        start_time = time.time()
        reseau = self.connexion.nettoyer_adresse_reseau(self.input_reseau.text())

        if not reseau:
            self.label_statut.setText("Erreur : réseau invalide.")
            return

        self.liste_martys.clear()
        self.label_statut.setText(f"Recherche sur {reseau}.x...")

        try:
            martys = self.connexion.rechercher_martys(reseau)
            if not martys:
                self.label_statut.setText(f"Recherche terminée en {(time.time()-start_time):.2f} secondes. Aucun Marty trouvé.")
                return

            for marty in martys:
                item = QListWidgetItem(f"{marty['nom']} - {marty['ip']} en {(time.time()-start_time):.2f} secondes.")
                item.setData(1000, marty["ip"])
                self.liste_martys.addItem(item)

            self.label_statut.setText(f"{len(martys)} Marty(s) trouvé(s).")

        except Exception as e:
            self.label_statut.setText(f"Erreur recherche : {e}")

    def connecter_selection(self):
        item = self.liste_martys.currentItem()

        if item is None:
            self.label_statut.setText("Erreur : sélectionne un Marty.")
            return

        ip = item.data(1000)
        self.connecter_a_ip(ip)

    def connecter_a_ip(self, ip):
        try:
            self.connexion.connecter(ip)
            self.label_statut.setText(f"Connecté à Marty : {ip}")
        except Exception as e:
            self.label_statut.setText(f"Erreur connexion : {e}")

    def deconnecter(self):
        try:
            self.connexion.deconnecter()
            self.label_statut.setText("Statut : déconnecté")
        except Exception as e:
            self.label_statut.setText(f"Erreur déconnexion : {e}")