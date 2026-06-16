from datetime import datetime
import json
import os
import math
import time
from random import randint

FICHIER_CALIBRATION_DEFAUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration_couleurs.json")

class CalibrateurCouleurs:
    def __init__(self, connexion=None, nom_fichier=FICHIER_CALIBRATION_DEFAUT):
        self.connexion = connexion
        self.nom_fichier = nom_fichier
        self.mesures = []

        self.charger_calibration()


    def _nom_capteur_couleur(self) -> str:
        """
        Découvre le nom réel de l'add-on capteur couleur déclaré par le robot.
        """
        addons = self.connexion.marty.get_add_ons_status()
        for addon in addons.values():
            if isinstance(addon, dict) and addon.get('whoAmI', '').lower() == 'coloursensor':
                return addon['name']
        raise RuntimeError(
            "Aucun capteur couleur trouvé. "
            "Vérifiez que le capteur est branché et reconnu par le robot."
        )

    def lire_valeur_brute(self):
        """
        Lit la valeur HEX du capteur couleur Marty.
        Retourne une chaîne "rrggbb".
        """
        if self.connexion is None:
            raise RuntimeError("Impossible de communique avec Marty : aucune connexion fournie")

        if not self.connexion.is_connected():
            raise RuntimeError("Marty n'est pas connecté")

        nom = self._nom_capteur_couleur()
        valeur_hex = self.connexion.marty.get_color_sensor_hex(nom)

        return self.nettoyer_hex(valeur_hex)


    def ajouter_mesure(self, couleur_reelle, eclairage, valeur_brute=None):
        """
        Enregistre une mesure de calibration et la sauvegarde dans le JSON.

        couleur_reelle : ex "Rouge", "Bleu", "Noir"
        eclairage      : ex "Normal", "Très lumineux"
        valeur_brute   : optionnel — hex brut, utile pour tester sans robot
        """

        if valeur_brute is None:
            valeur_brute = self.lire_valeur_brute()

        valeur_brute = self.nettoyer_hex(valeur_brute)

        mesure = {
            "couleur": couleur_reelle.strip(),
            "eclairage": eclairage.strip(),
            "hex": valeur_brute,
            "rgb": self.hex_vers_rgb(valeur_brute),
            "date": datetime.now().isoformat(timespec="seconds")
        }

        self.mesures.append(mesure)
        self.sauvegarder_calibration()

        return mesure


    def get_couleur(self, seuil_max=80):
        """
        Lit le capteur et renvoie le nom de la couleur la plus proche (str).

        Retourne "inconnue" si aucune calibration ou si la distance dépasse seuil_max.
        """
        valeur_brute = self.lire_valeur_brute()
        nom, _ = self.trouver_couleur_depuis_hex(valeur_brute, seuil_max)
        return nom


    def trouver_couleur_depuis_hex(self, valeur_hex=None, seuil_max=80):
        """
        Trouve la couleur calibrée la plus proche d'une valeur HEX.
        Retourne toujours un tuple (nom: str, distance: float).

        Exemple :
            calibrateur.trouver_couleur_depuis_hex("871819")  ->  ("Rouge", 12.4)
        """
        if not self.mesures:
            return "inconnue", 0.0

        if valeur_hex is None:
            valeur_hex = self.lire_valeur_brute()

        valeur_hex = self.nettoyer_hex(valeur_hex)
        rgb_lu = self.hex_vers_rgb(valeur_hex)

        meilleure_couleur = ""
        meilleure_distance = float("inf")

        for mesure in self.mesures:
            rgb_ref = tuple(mesure["rgb"])
            distance = self.distance_rgb(rgb_lu, rgb_ref)

            if distance < meilleure_distance:
                meilleure_distance = distance
                meilleure_couleur = mesure["couleur"]

        if meilleure_distance > seuil_max:
            return "inconnue", round(meilleure_distance, 2)

        return meilleure_couleur, round(meilleure_distance, 2)


    #### Gestion du fichier de calibration
    def sauvegarder_calibration(self):
        with open(self.nom_fichier, "w", encoding="utf-8") as fichier:
            json.dump(self.mesures, fichier, indent=4, ensure_ascii=False)

    def charger_calibration(self):
        if not os.path.exists(self.nom_fichier):
            self.mesures = []
            return

        try:
            with open(self.nom_fichier, "r", encoding="utf-8") as fichier:
                self.mesures = json.load(fichier)

        except Exception:
            self.mesures = []


    #### Helpers ####
    @staticmethod
    def nettoyer_hex(valeur_hex):
        """
        Normalise une valeur HEX vers "rrggbb" (6 chiffres, minuscules, sans préfixe).
        """
        valeur_hex = str(valeur_hex).strip().lower()
        valeur_hex = valeur_hex.replace("#", "")
        valeur_hex = valeur_hex.replace("0x", "")

        if len(valeur_hex) > 6:
            valeur_hex = valeur_hex[-6:]

        if len(valeur_hex) != 6:
            raise ValueError(f"Valeur HEX invalide : {valeur_hex}")

        int(valeur_hex, 16)

        return valeur_hex

    @staticmethod
    def hex_vers_rgb(clean_valeur_hex):
        """
        Converti une valeur hexadécimal en valeur RGB
        Ex: ff34ad -> [255, 52, 173]
        """
        r = int(clean_valeur_hex[0:2], 16)
        g = int(clean_valeur_hex[2:4], 16)
        b = int(clean_valeur_hex[4:6], 16)
        return [r, g, b]

    @staticmethod
    def distance_rgb(rgb1, rgb2):
        """
        Calcul savant de la distance entre deux couleurs
        """
        return math.sqrt(
            (rgb1[0] - rgb2[0]) ** 2 +
            (rgb1[1] - rgb2[1]) ** 2 +
            (rgb1[2] - rgb2[2]) ** 2
        )

    def generer_hex(self):
        """Génère une couleur aléatoire (outil de debug)."""
        return "#{:06x}".format(randint(0, 0xFFFFFF))


if __name__ == "__main__":
    calibrateur = CalibrateurCouleurs(connexion=None)
    for color, hex_color in [
        ("Rouge",   "#ff0000"),
        ("Vert",    "#00ff00"),
        ("Bleu",    "#0000ff"),
        ("Jaune",   "#ffff00"),
        ("Magenta", "#ff00ff"),
        ("Cyan",    "#00ffff"),
        ("Blanc",   "#ffffff"),
        ("Noir",    "#000000"),
    ]:
        mesure = calibrateur.ajouter_mesure(
            couleur_reelle=color,
            eclairage="Lumineux",
            valeur_brute=hex_color
        )
        print(mesure)

    while True:
        random_hex = calibrateur.generer_hex()
        nom, distance = calibrateur.trouver_couleur_depuis_hex(random_hex, 80)
        print(f"For {random_hex} the guess is {nom} avec une distance de {distance}")
        time.sleep(0.1)
