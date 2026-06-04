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
        self.martys_trouves = []

        layout = QVBoxLayout()

        self.label_statut = QLabel("Statut : non connecté")
        layout.addWidget(self.label_statut)

        ligne_ip = QHBoxLayout()

        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText("IP manuelle du Marty ex : 192.168.0.104")

        self.bouton_connexion = QPushButton("Connexion manuelle")
        self.bouton_connexion.clicked.connect(self.connecter_ip_manuelle)

        ligne_ip.addWidget(self.input_ip)
        ligne_ip.addWidget(self.bouton_connexion)

        layout.addLayout(ligne_ip)

        self.bouton_recherche = QPushButton("Rechercher les Marty sur le réseau")
        self.bouton_recherche.clicked.connect(self.rechercher_martys)
        layout.addWidget(self.bouton_recherche)

        self.liste_martys = QListWidget()
        layout.addWidget(self.liste_martys)

        self.bouton_connecter_selection = QPushButton("Se connecter au Marty sélectionné")
        self.bouton_connecter_selection.clicked.connect(self.connecter_marty_selectionne)
        layout.addWidget(self.bouton_connecter_selection)

        self.bouton_deconnexion = QPushButton("Déconnecter")
        self.bouton_deconnexion.clicked.connect(self.deconnecter)
        layout.addWidget(self.bouton_deconnexion)

        self.setLayout(layout)

    def connecter_ip_manuelle(self):
        ip = self.input_ip.text().strip()

        if not ip:
            self.label_statut.setText("Erreur : entre une IP.")
            return

        self.connecter_a_ip(ip)

    def rechercher_martys(self):
        self.liste_martys.clear()
        self.martys_trouves = []

        reseau = self.connexion.detecter_reseau()
        if reseau is None:
            self.label_statut.setText("Adresse IP non trouvée.")
            return

        self.label_statut.setText(f"Adresse IP trouvée ({reseau}), recherche de Marty en cours...")

        try:
            self.martys_trouves = self.connexion.rechercher_martys(reseau)

            if not self.martys_trouves:
                self.label_statut.setText("Aucun Marty trouvé.")
                return

            for marty in self.martys_trouves:
                texte = f"{marty['nom']} - {marty['ip']}"
                item = QListWidgetItem(texte)
                item.setData(1000, marty["ip"])
                self.liste_martys.addItem(item)

            self.label_statut.setText(
                f"{len(self.martys_trouves)} Marty(s) trouvé(s)."
            )

        except Exception as e:
            self.label_statut.setText(f"Erreur recherche : {e}")

    def connecter_marty_selectionne(self):
        item = self.liste_martys.currentItem()

        if item is None:
            self.label_statut.setText("Erreur : sélectionne un Marty dans la liste.")
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