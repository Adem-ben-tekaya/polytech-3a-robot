import time
from PyQt6.QtCore import QObject, pyqtSignal


class ChoreoWorker(QObject):
    """Exécute une chorégraphie pas à pas dans un QThread.

    Signaux :
        log(str)                          — message à afficher dans le journal
        step_done(num, direction, bras, expression) — un pas terminé
        finished()                        — chorégraphie terminée ou arrêtée
        error(str)                        — erreur fatale
    """

    log = pyqtSignal(str)
    step_done = pyqtSignal(int, str, str, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, mouvement, dance: dict, nb_steps: int, offline: bool = False):
        super().__init__()
        self._mouvement = mouvement
        self._dance = dance
        self._nb_steps = nb_steps
        self._offline = offline
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        moves = self._dance['moves']
        actions = self._dance['actions']
        nb_moves = len(moves)

        if nb_moves == 0:
            self.error.emit("Aucun mouvement dans le fichier .dance")
            return

        try:
            for step in range(self._nb_steps):
                if self._stop:
                    self.log.emit("Chorégraphie arrêtée.")
                    break

                move = moves[step % nb_moves]
                direction = move['direction']
                count = move['count']
                noms = {'U': 'avant', 'B': 'arrière', 'L': 'gauche', 'R': 'droite'}
                self.log.emit(
                    f"Pas {step + 1}/{self._nb_steps} : {count}x {noms.get(direction, direction)}"
                )

                if not self._offline:
                    self._mouvement.marcher(direction, count)
                    r, g, b = self._mouvement.get_couleur_raw()
                    self.log.emit(f"  Capteur couleur → R={r} G={g} B={b}")

                # La correspondance RGB→code couleur sera gérée par CalibrateurCouleurs
                # Pour l'instant on utilise 'N' comme placeholder
                couleur = 'N'

                action = actions.get(couleur, {'arms': [], 'expression': 'XNT'})
                arms = action['arms']
                expression = action['expression']
                arms_str = '+'.join(arms) if arms else 'aucun'

                self.log.emit(f"  Couleur: {couleur} | Bras: {arms_str} | Expression: {expression}")

                if not self._offline:
                    self._mouvement.set_bras(arms)
                    self._mouvement.set_expression(expression)
                    time.sleep(1.0)
                    self._mouvement.reset_position()
                else:
                    time.sleep(0.05)

                self.step_done.emit(step + 1, direction, arms_str, expression)
            else:
                self.log.emit("Chorégraphie terminée.")

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
