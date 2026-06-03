from datetime import datetime
import math


class CalibrateurCouleurs:
    def __init__(self, nom_fichier="Calibration des couleurs.txt"):
        self.nom_fichier = nom_fichier
        self.resultats = []
        self.numero_couleur = 1

    def enregistrer_mesure(self, nom_couleur, condition, valeur_hex):
        valeur_hex = self.nettoyer_hex(valeur_hex)

        mesure = {
            "numero": self.numero_couleur,
            "nom": nom_couleur,
            "condition": condition,
            "hex": valeur_hex
        }

        self.resultats.append(mesure)

    def couleur_suivante(self):
        self.numero_couleur += 1

    def nettoyer_hex(self, valeur_hex):
        valeur_hex = str(valeur_hex).strip().replace("#", "")

        # Certains capteurs renvoient parfois 7 caractères, ex : 1377c3d.
        # On garde les 6 derniers pour obtenir un RGB exploitable.
        if len(valeur_hex) > 6:
            valeur_hex = valeur_hex[-6:]

        return valeur_hex.lower()

    def hex_vers_rgb(self, valeur_hex):
        valeur_hex = self.nettoyer_hex(valeur_hex)

        if len(valeur_hex) != 6:
            raise ValueError(f"HEX invalide : {valeur_hex}")

        r = int(valeur_hex[0:2], 16)
        g = int(valeur_hex[2:4], 16)
        b = int(valeur_hex[4:6], 16)

        return r, g, b

    def distance_rgb(self, rgb1, rgb2):
        return math.sqrt(
            (rgb1[0] - rgb2[0]) ** 2 +
            (rgb1[1] - rgb2[1]) ** 2 +
            (rgb1[2] - rgb2[2]) ** 2
        )

    def calculer_zones(self, marge_minimale=25):
        zones = {}

        for mesure in self.resultats:
            nom = mesure["nom"]
            rgb = self.hex_vers_rgb(mesure["hex"])

            if nom not in zones:
                zones[nom] = {
                    "mesures_rgb": [],
                    "centre_rgb": None,
                    "rayon": 0
                }

            zones[nom]["mesures_rgb"].append(rgb)

        for nom, zone in zones.items():
            mesures = zone["mesures_rgb"]

            moyenne_r = sum(rgb[0] for rgb in mesures) / len(mesures)
            moyenne_g = sum(rgb[1] for rgb in mesures) / len(mesures)
            moyenne_b = sum(rgb[2] for rgb in mesures) / len(mesures)

            centre = (
                round(moyenne_r),
                round(moyenne_g),
                round(moyenne_b)
            )

            distances = [
                self.distance_rgb(rgb, centre)
                for rgb in mesures
            ]

            rayon = max(distances) if distances else 0
            rayon = round(rayon + marge_minimale)

            zone["centre_rgb"] = centre
            zone["rayon"] = rayon

        return zones

    def detecter_couleur(self, valeur_hex):
        rgb_lu = self.hex_vers_rgb(valeur_hex)
        zones = self.calculer_zones()

        meilleure_couleur = None
        meilleure_distance = float("inf")

        for nom, zone in zones.items():
            distance = self.distance_rgb(rgb_lu, zone["centre_rgb"])

            if distance <= zone["rayon"] and distance < meilleure_distance:
                meilleure_couleur = nom
                meilleure_distance = distance

        if meilleure_couleur is None:
            return "inconnue"

        return meilleure_couleur

    def sauvegarder(self):
        zones = self.calculer_zones()

        with open(self.nom_fichier, "w", encoding="utf-8") as fichier:
            fichier.write("Calibration des couleurs Marty\n")
            fichier.write(f"Date : {datetime.now()}\n")
            fichier.write("=" * 40 + "\n\n")

            fichier.write("MESURES BRUTES\n")
            fichier.write("=" * 40 + "\n\n")

            for mesure in self.resultats:
                fichier.write(f"Couleur #{mesure['numero']}\n")
                fichier.write(f"Nom : {mesure['nom']}\n")
                fichier.write(f"Condition : {mesure['condition']}\n")
                fichier.write(f"Valeur HEX : {mesure['hex']}\n")
                fichier.write("-" * 30 + "\n")

            fichier.write("\n\nZONES DE RECONNAISSANCE\n")
            fichier.write("=" * 40 + "\n\n")

            for nom, zone in zones.items():
                fichier.write(f"Nom : {nom}\n")
                fichier.write(f"Centre RGB : {zone['centre_rgb']}\n")
                fichier.write(f"Rayon : {zone['rayon']}\n")
                fichier.write(f"Mesures RGB : {zone['mesures_rgb']}\n")
                fichier.write("-" * 30 + "\n")

        return self.nom_fichier