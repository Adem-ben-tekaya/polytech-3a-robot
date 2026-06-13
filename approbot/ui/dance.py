from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QTextEdit,
    QScrollArea,
    QSizePolicy
)
from PyQt6.QtCore import QThread
from approbot.mouvement_marty import MouvementMarty
from approbot.dance_parser import parse as parse_dance, resume as resume_dance
from approbot.choreo_worker import ChoreoWorker


class OngletDance(QWidget):
    def __init__(self, connexion, calibrateur, serveur=None):
        super().__init__()

        self.connexion = connexion
        self.serveur = serveur
        self.mouvement = MouvementMarty(connexion, calibrateur)
        self._dance = None
        self._worker = None
        self._thread = None

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # ── Fichier ──────────────────────────────────────────────────────
        groupe_fichier = QGroupBox("Fichier .dance")
        layout_fichier = QHBoxLayout()

        self.label_fichier = QLabel("Aucun fichier chargé")
        self.label_fichier.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bouton_charger = QPushButton("Charger .dance")
        bouton_charger.setFixedWidth(140)
        bouton_charger.clicked.connect(self._charger_dance)

        layout_fichier.addWidget(self.label_fichier)
        layout_fichier.addWidget(bouton_charger)
        groupe_fichier.setLayout(layout_fichier)
        layout.addWidget(groupe_fichier)

        # ── Aperçu de la chorégraphie ─────────────────────────────────────
        groupe_apercu = QGroupBox("Chorégraphie chargée")
        layout_apercu = QVBoxLayout()

        self.texte_apercu = QTextEdit()
        self.texte_apercu.setReadOnly(True)
        self.texte_apercu.setPlaceholderText("Le contenu du fichier .dance apparaîtra ici après chargement.")
        self.texte_apercu.setMaximumHeight(160)
        layout_apercu.addWidget(self.texte_apercu)

        groupe_apercu.setLayout(layout_apercu)
        layout.addWidget(groupe_apercu)

        # ── Contrôle ─────────────────────────────────────────────────────
        groupe_controle = QGroupBox("Contrôle")
        layout_controle = QVBoxLayout()

        ligne_boutons = QHBoxLayout()
        self.bouton_lancer = QPushButton("Lancer")
        self.bouton_lancer.clicked.connect(self._lancer)
        self.bouton_lancer.setEnabled(False)

        self.bouton_arreter = QPushButton("Arrêter")
        self.bouton_arreter.clicked.connect(self._arreter)
        self.bouton_arreter.setEnabled(False)

        ligne_boutons.addWidget(self.bouton_lancer)
        ligne_boutons.addWidget(self.bouton_arreter)
        layout_controle.addLayout(ligne_boutons)

        self.label_statut = QLabel("Statut : —")
        layout_controle.addWidget(self.label_statut)

        groupe_controle.setLayout(layout_controle)
        layout.addWidget(groupe_controle)

        # ── Résultats ─────────────────────────────────────────────────────
        groupe_resultats = QGroupBox("Résultats d'exécution")
        layout_resultats = QVBoxLayout()

        self.log_execution = QTextEdit()
        self.log_execution.setReadOnly(True)
        self.log_execution.setPlaceholderText("Les résultats pas à pas apparaîtront ici.")
        layout_resultats.addWidget(self.log_execution)

        bouton_effacer = QPushButton("Effacer les résultats")
        bouton_effacer.setFixedWidth(180)
        bouton_effacer.clicked.connect(self.log_execution.clear)
        layout_resultats.addWidget(bouton_effacer)

        groupe_resultats.setLayout(layout_resultats)
        layout.addWidget(groupe_resultats)

        self.setLayout(layout)

    # ── Slots ─────────────────────────────────────────────────────────────

    def _charger_dance(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un fichier .dance", "", "Fichiers dance (*.dance)"
        )
        if not path:
            return
        try:
            self._dance = parse_dance(path)
            nom = path.replace('\\', '/').split('/')[-1]
            self.label_fichier.setText(nom)
            self.texte_apercu.setPlainText(resume_dance(self._dance))
            self.bouton_lancer.setEnabled(True)
            self.label_statut.setText(f"Fichier chargé : {nom}")
        except Exception as e:
            self.label_statut.setText(f"Erreur lecture .dance : {e}")

    def _lancer(self):
        if not self.connexion.is_connected():
            self.label_statut.setText("Statut : robot non connecté")
            return
        if self._dance is None:
            return

        nb_steps = len(self._dance['moves'])

        if self.serveur is not None and self.serveur.est_enregistre():
            try:
                nb_steps = self.serveur.start()
                self.log_execution.append(f"Serveur : {nb_steps} pas demandés\n")
            except Exception as e:
                self.label_statut.setText(f"Erreur serveur start : {e}")
                return

        self.log_execution.clear()
        self.log_execution.append(f"Démarrage — {nb_steps} pas\n")

        self._thread = QThread()
        self._worker = ChoreoWorker(self.mouvement, self._dance, nb_steps, serveur=self.serveur)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._on_log)
        self._worker.step_done.connect(self._on_step_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._on_finished)
        self._thread.finished.connect(self._thread.deleteLater)

        self.bouton_lancer.setEnabled(False)
        self.bouton_arreter.setEnabled(True)
        self.label_statut.setText("Chorégraphie en cours...")
        self._thread.start()

    def _arreter(self):
        if self._worker is not None:
            self._worker.stop()

    def _on_log(self, message: str):
        self.log_execution.append(message)

    def _on_step_done(self, num: int, direction: str, bras: str, expression: str):
        noms = {'U': 'avant', 'B': 'arrière', 'L': 'gauche', 'R': 'droite'}
        self.label_statut.setText(
            f"Pas {num} — {noms.get(direction, direction)} | bras: {bras} | expression: {expression}"
        )
        self.log_execution.append(
            f"✓ Pas {num} terminé : dir={noms.get(direction, direction)}  bras={bras}  exp={expression}\n"
        )

    def _on_error(self, message: str):
        self.log_execution.append(f"\nErreur : {message}")
        self.label_statut.setText(f"Erreur : {message}")

    def _on_finished(self):
        self.bouton_lancer.setEnabled(self._dance is not None)
        self.bouton_arreter.setEnabled(False)
        self._worker = None
        self._thread = None
        if "en cours" in self.label_statut.text():
            self.label_statut.setText("Statut : chorégraphie terminée")

    def cleanup(self):
        """Arrête proprement le thread si l'app se ferme pendant une exécution."""
        if self._worker is not None:
            self._worker.stop()
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
