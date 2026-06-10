import json
import os
import math
from datetime import datetime

FICHIER_CALIBRATION_DEFAUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration_couleurs.json")

class CalibrateurCouleurs:
    def __init__(self, connexion=None, nom_fichier=FICHIER_CALIBRATION_DEFAUT):
        self.connexion = connexion
        self.nom_fichier = nom_fichier
        self.mesures = []

        self.charger_calibration()


    def lire_valeur_brute(self, pied="left"):
        """
        Lit la valeur la plus exploitable du capteur couleur Marty.

        Pour notre projet, on utilise la valeur HEX car elle représente déjà
        une couleur complète sous forme RRGGBB.

        Exemple retourné :
        "871819"
        """
        if self.connexion is None:
            raise RuntimeError("Impossible de lire Marty : aucune connexion fournie")
        
        if not self.connexion.is_connected():
            raise RuntimeError("Marty n'est pas connecté")

        valeur_hex = self.connexion.marty.get_color_sensor_hex(pied)

        return self.nettoyer_hex(valeur_hex)


    def ajouter_mesure(self, couleur_reelle, eclairage, valeur_brute=None, pied="left"):
        """
        Ajoute une mesure dans la calibration.

        couleur_reelle : ex "Rouge", "Bleu", "Vert"
        eclairage : "Lumineux", "Normal", "Sombre"
        valeur_brute : optionnel, utile pour tester sans robot
        pied : "left" ou "right"
        """

        if valeur_brute is None:
            valeur_brute = self.lire_valeur_brute(pied)

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


    def get_couleur(self, pied="left", seuil_max=80):
        """
        Lit le capteur et renvoie le nom de la couleur la plus proche.

        Exemple :
        capteur -> "FF6534"
        retour  -> "Rouge"
        """
        valeur_brute = self.lire_valeur_brute(pied)
        return self.trouver_couleur_depuis_hex(valeur_brute, seuil_max)

    def trouver_couleur_depuis_hex(self, valeur_hex=None, seuil_max=80):
        """
        Trouve la couleur calibrée la plus proche d'une valeur HEX.

        Cette fonction est très utile pour débugger sans robot :
        calibrateur.trouver_couleur_depuis_hex("871819")
        """
        if not self.mesures:
            return "inconnue/aucun fichier de calibration n'a été trouvé"
        
        if valeur_hex == None:
            valeur_hex = self.lire_valeur_brute()

        valeur_hex = self.nettoyer_hex(valeur_hex)
        rgb_lu = self.hex_vers_rgb(valeur_hex)

        meilleure_couleur = "inconnue/couleur par defaut"
        meilleure_distance = float("inf")

        for mesure in self.mesures:
            rgb_ref = tuple(mesure["rgb"])
            distance = self.distance_rgb(rgb_lu, rgb_ref)

            if distance < meilleure_distance:
                meilleure_distance = distance
                meilleure_couleur = mesure["couleur"]

        if meilleure_distance > seuil_max:
            return "inconnue/seuil depasse"

        return meilleure_couleur
    
    # Gestion du fichier de calibration
    def sauvegarder_calibration(self):
        """
        Écrit dans le fichier de calibrations les mesures 
        enregistrer durant la session de calibration
        """
        with open(self.nom_fichier, "w", encoding="utf-8") as fichier:
            json.dump(self.mesures, fichier, indent=4, ensure_ascii=False)

    def charger_calibration(self):
        """
        Créer une liste dans laquelle se trouvera l'intégralité des mesures 
        enregistrer durant la session de calibration

        Renvoi une liste vide si aucune calibration n'a été trouvée
        """
        if not os.path.exists(self.nom_fichier):
            self.mesures = []
            return

        try:
            with open(self.nom_fichier, "r", encoding="utf-8") as fichier:
                self.mesures = json.load(fichier)

        except Exception:
            self.mesures = []

    # Helpers
    @staticmethod
    def nettoyer_hex(valeur_hex):
        """
        Nettoie une valeur HEX.

        Accepte :
        "#FF6534"
        "FF6534"
        "0xff6534"
        "aFf6534"

        Retourne toujours :
        "ff6534"
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

        r = int(clean_valeur_hex[0:2], 16)
        g = int(clean_valeur_hex[2:4], 16)
        b = int(clean_valeur_hex[4:6], 16)

        return [r, g, b]

    @staticmethod
    def distance_rgb(rgb1, rgb2):
        return math.sqrt(
            (rgb1[0] - rgb2[0]) ** 2 +
            (rgb1[1] - rgb2[1]) ** 2 +
            (rgb1[2] - rgb2[2]) ** 2
        )
    
if __name__ == "__main__":
    calibrateur = CalibrateurCouleurs(connexion=None)
    for color,hex_color in [
        ("Rouge","#ff0000"),
        ("Vert","#00ff00"),
        ("Bleu","#0000ff"),
        ("Jaune","#ffff00"),
        ("Magenta","#ff00ff"),
        ("Cyan","#00ffff"),
        ("Blanc","#ffffff"),
        ("Noir","#000000")
        ]:

        mesure = calibrateur.ajouter_mesure(
            couleur_reelle=color,
            eclairage="Lumineux",
            valeur_brute= hex_color
        )
        print(mesure)

    detected_color = calibrateur.trouver_couleur_depuis_hex("#c54949", 80)
    print(detected_color)
