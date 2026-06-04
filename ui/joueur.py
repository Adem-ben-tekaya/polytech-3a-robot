from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox
)
from Joueur.mouvement_marty import MouvementMarty


class OngletJoueur(QWidget):
    def __init__(self, connexion, calibrateur):
        super().__init__()

        self.connexion = connexion
        self.calibrateur = calibrateur
        self.mouvement = MouvementMarty(connexion, calibrateur)

        layout = QVBoxLayout()

        self.label_statut = QLabel("Statut : —")
        layout.addWidget(self.label_statut)

        # --- Marche ---
        groupe_marche = QGroupBox("Marche")
        grille_marche = QVBoxLayout()

        ligne_avancer = QHBoxLayout()
        bouton_avancer = QPushButton("Avancer")
        bouton_avancer.clicked.connect(lambda: self._marcher('U'))
        ligne_avancer.addWidget(bouton_avancer)
        grille_marche.addLayout(ligne_avancer)

        ligne_laterale = QHBoxLayout()
        bouton_gauche = QPushButton("Gauche")
        bouton_gauche.clicked.connect(lambda: self._marcher('L'))
        bouton_droite = QPushButton("Droite")
        bouton_droite.clicked.connect(lambda: self._marcher('R'))
        ligne_laterale.addWidget(bouton_gauche)
        ligne_laterale.addWidget(bouton_droite)
        grille_marche.addLayout(ligne_laterale)

        ligne_reculer = QHBoxLayout()
        bouton_reculer = QPushButton("Reculer")
        bouton_reculer.clicked.connect(lambda: self._marcher('B'))
        ligne_reculer.addWidget(bouton_reculer)
        grille_marche.addLayout(ligne_reculer)

        groupe_marche.setLayout(grille_marche)
        layout.addWidget(groupe_marche)

        # --- Bras ---
        groupe_bras = QGroupBox("Bras")
        ligne_bras = QHBoxLayout()

        for label, tokens in [
            ("Bras G haut",   ['ALU']),
            ("Bras G arrière",['ALB']),
            ("Bras D haut",   ['ARU']),
            ("Bras D arrière",['ARB']),
            ("Les deux haut", ['ALU', 'ARU']),
        ]:
            b = QPushButton(label)
            b.clicked.connect(lambda checked, t=tokens: self._set_bras(t))
            ligne_bras.addWidget(b)

        groupe_bras.setLayout(ligne_bras)
        layout.addWidget(groupe_bras)

        # --- Expression ---
        groupe_exp = QGroupBox("Expression")
        ligne_exp = QHBoxLayout()

        for label, token in [
            ("Neutre",   'XNT'),
            ("Content",  'XHP'),
            ("Triste",   'XSD'),
            ("En colère",'XNG'),
            ("Joueur",   'XDN'),
        ]:
            b = QPushButton(label)
            b.clicked.connect(lambda checked, t=token: self._set_expression(t))
            ligne_exp.addWidget(b)

        groupe_exp.setLayout(ligne_exp)
        layout.addWidget(groupe_exp)

        # --- Capteurs ---
        groupe_capteurs = QGroupBox("Capteurs")
        ligne_capteurs = QHBoxLayout()

        bouton_couleur = QPushButton("Lire couleur")
        bouton_couleur.clicked.connect(self._lire_couleur)
        bouton_batterie = QPushButton("Lire batterie")
        bouton_batterie.clicked.connect(self._lire_batterie)

        ligne_capteurs.addWidget(bouton_couleur)
        ligne_capteurs.addWidget(bouton_batterie)
        groupe_capteurs.setLayout(ligne_capteurs)
        layout.addWidget(groupe_capteurs)

        layout.addStretch()
        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Slots privés
    # ------------------------------------------------------------------

    def _marcher(self, direction: str):
        if not self.connexion.is_connected():
            self.label_statut.setText("Statut : robot non connecté")
            return
        try:
            self.mouvement.marcher(direction, 1)
            noms = {'U': 'avant', 'B': 'arrière', 'L': 'gauche', 'R': 'droite'}
            self.label_statut.setText(f"Marche : {noms.get(direction, direction)}")
        except Exception as e:
            self.label_statut.setText(f"Erreur marche : {e}")

    def _set_bras(self, tokens: list):
        if not self.connexion.is_connected():
            self.label_statut.setText("Statut : robot non connecté")
            return
        try:
            self.mouvement.set_bras(tokens)
            self.label_statut.setText(f"Bras : {'+'.join(tokens)}")
        except Exception as e:
            self.label_statut.setText(f"Erreur bras : {e}")

    def _set_expression(self, token: str):
        if not self.connexion.is_connected():
            self.label_statut.setText("Statut : robot non connecté")
            return
        try:
            self.mouvement.set_expression(token)
            self.label_statut.setText(f"Expression : {token}")
        except Exception as e:
            self.label_statut.setText(f"Erreur expression : {e}")

    def _lire_couleur(self):
        if not self.connexion.is_connected():
            self.label_statut.setText("Statut : robot non connecté")
            return
        try:
            couleur = self.mouvement.dtecter_couleur("left")
            self.label_statut.setText(f"Couleur capteur : {couleur}")
        except Exception as e:
            self.label_statut.setText(f"Erreur capteur couleur : {e}")

    def _lire_batterie(self):
        if not self.connexion.is_connected():
            self.label_statut.setText("Statut : robot non connecté")
            return
        try:
            pct = self.mouvement.get_batterie()
            self.label_statut.setText(f"Batterie : {pct}%")
        except Exception as e:
            self.label_statut.setText(f"Erreur batterie : {e}")
