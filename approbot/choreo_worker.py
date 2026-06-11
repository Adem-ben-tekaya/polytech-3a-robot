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

    def __init__(self, mouvement, dance_or_dance_file_path, nb_steps: int, serveur=None, offline: bool = False):
        super().__init__()

        self._mouvement = mouvement
        self._nb_steps = nb_steps
        self._serveur = serveur
        self._offline = offline
        self._stop = False

        if dance_or_dance_file_path is None:
            raise ValueError("Chargez un fichier .dance avant de lancer une danse.")

        if isinstance(dance_or_dance_file_path, dict):
            self._dance = dance_or_dance_file_path
        else:
            self._dance = charger_dance(dance_or_dance_file_path)


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
                noms = {
                    'U': 'avant', 
                    'B': 'arrière', 
                    'L': 'gauche', 
                    'R': 'droite'
                    }
                
                self.log.emit(
                    f"Pas {step + 1}/{self._nb_steps} : {count}x {noms.get(direction, direction)}"
                )

                if not self._offline:
                    self._mouvement.marcher(direction, count)

                    couleur_lue = self._mouvement.get_couleur("left")
                    couleur = self.normaliser_couleur(couleur_lue)
                    self.log.emit(f"  Couleur détectée : {couleur_lue} -> code {couleur}")

                else :
                    couleur = 'N'
                    self.log.emit("  Mode offline (Marty non conecté) : couleur forcée à N")
                

                action = actions.get(
                    couleur, 
                    {'arms': [], 'expression': 'XNT'}
                )
                
                arms = action['arms']
                expression = action['expression']
                
                arms_str = '+'.join(arms) if arms else 'aucun'

                self.log.emit(f"  Action : couleur: {couleur}, bras: {arms_str}, expression: {expression}")

                if not self._offline:
                    self._mouvement.set_bras(arms)
                    self._mouvement.set_expression(expression)

                if self._serveur is not None and hasattr(self, "_serveur") :
                    points = self._serveur.step(
                        couleur=couleur,
                        bras=arms_str,
                        expression=expression
                    )

                    score = self._serveur.score()

                    self.log.emit(
                        f"  Serveur : +{points} point(s), score total = {score}"
                    )

                time.sleep(0.5)

                self.step_done.emit(step + 1, direction, arms_str, expression)
            else:
                self.log.emit("Chorégraphie terminée.")

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

    @staticmethod
    def normaliser_couleur(couleur):
        """
        Convertit une couleur lisible en code utilisé par le serveur/.dance.

        Exemple :
        Rouge -> R
        Bleu  -> B
        Noir  -> N
        """

        if couleur is None:
            return "N"

        couleur = str(couleur).strip().lower()

        if len(couleur) == 1:
            return couleur.upper()

        correspondances = {
            "rouge": "R",
            "red": "R",

            "bleu": "B",
            "blue": "B",

            "vert": "G",
            "green": "G",

            "jaune": "Y",
            "yellow": "Y",

            "noir": "N",
            "black": "N",

            "blanc": "W",
            "white": "W",

            "cyan": "C",

            "magenta": "P",
            "violet": "P",
            "purple": "P",
        }

        return correspondances.get(couleur)


def charger_dance(chemin_fichier):
    """
    Charge un fichier .dance simple.

    Format attendu exemple :

    SEQ 1
    1U
    1L
    2B
    ACT
    N XNT
    R ALU ARU XNG
    B XSD
    G XHP
    """

    dance = {
        "moves": [],
        "actions": {}
    }

    section = None

    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            ligne = ligne.strip()

            if not ligne or ligne.startswith("#"):
                continue

            if ligne.startswith("SEQ"):
                section = "moves"
                continue

            if ligne.startswith("ACT"):
                section = "actions"
                continue

            if section == "moves":
                # Exemple : 1U, 2B, 3L
                count = int(ligne[:-1])
                direction = ligne[-1]

                dance["moves"].append({
                    "count": count,
                    "direction": direction
                })

            elif section == "actions":
                morceaux = ligne.split()

                couleur = morceaux[0]
                tokens = morceaux[1:]

                arms = []
                expression = "XNT"

                for token in tokens:
                    if token.startswith("A"):
                        arms.append(token)
                    elif token.startswith("X"):
                        expression = token

                dance["actions"][couleur] = {
                    "arms": arms,
                    "expression": expression
                }

    return dance



def lancer_battle_console(ip_marty, ip_serveur, fichier_dance, nom_robot="Marty", offline=False):
    import sys
    import os

    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, racine)

    from approbot.connexion_marty import ConnexionMarty
    from approbot.calibrateur_couleurs import CalibrateurCouleurs
    from approbot.mouvement_marty import MouvementMarty
    from approbot.server_gets import RequetesServeur

    connexion = None
    mouvement = None
    serveur = RequetesServeur()

    try:
        dance = charger_dance(fichier_dance)

        print("Connexion au serveur...")
        serveur.definir_url(ip_serveur)

        version = serveur.verifier_connexion()
        print("Serveur OK :", version)

        rid = serveur.hello()
        print("Robot enregistré :", rid)

        serveur.nom_robot(nom_robot)
        print("Nom robot envoyé :", nom_robot)

        nb_steps = serveur.start()
        print("Nombre de pas à faire :", nb_steps)

        if offline:
            print("Mode offline : aucun Marty connecté.")
        else:
            if ip_marty is None:
                raise RuntimeError("IP Marty obligatoire si offline=False")

            print("Connexion au Marty...")
            connexion = ConnexionMarty()
            connexion.connecter(ip_marty)

            calibrateur = CalibrateurCouleurs(connexion)
            mouvement = MouvementMarty(connexion, calibrateur)

        worker = ChoreoWorker(
            mouvement=mouvement,
            dance_or_dance_file_path=dance,
            nb_steps=nb_steps,
            serveur=serveur,
            offline=offline
        )

        worker.log.connect(print)
        worker.error.connect(lambda msg: print("ERREUR :", msg))
        worker.finished.connect(lambda: print("Battle terminée."))

        worker.run()

    finally:
        try:
            serveur.deconnecter()
            print("Déconnexion serveur OK")
        except Exception:
            pass

        try:
            if connexion is not None:
                connexion.deconnecter()
                print("Déconnexion Marty OK")
        except Exception:
            pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Lancer une battle Marty sans interface graphique")

    parser.add_argument("--marty", required=False, default=None, help="IP du Marty")
    parser.add_argument("--serveur", required=True, help="IP du serveur arbitre")
    parser.add_argument("--dance", required=True, help="Chemin du fichier .dance")
    parser.add_argument("--nom", default="Marty", help="Nom du robot")
    parser.add_argument("--offline", action="store_true", help="Lance sans robot Marty")

    args = parser.parse_args()

    lancer_battle_console(
        ip_marty=args.marty,
        ip_serveur=args.serveur,
        fichier_dance=args.dance,
        nom_robot=args.nom,
        offline=args.offline
    )