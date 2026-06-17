from approbot.calibrateur_couleurs import CalibrateurCouleurs

JOINT_LEFT_ARM   = 6
JOINT_RIGHT_ARM  = 7
ARM_UP           = 100
ARM_BACK         = -100
STEP_LENGTH      = 40
STEP_TIME_MS     = 1500
SIDE_STEP_LENGTH = 500
SIDE_STEP_TIME   = 600


class MouvementMarty:

    def __init__(self, connexion, calibrateur):
        """
        connexion  : instance ConnexionMarty partagée avec les autres onglets
        calibrateur: instance CalibrateurCouleurs pour la lecture et la correspondance de couleur
        """
        self._connexion = connexion
        self._calibrateur = calibrateur
        
    def goat_dance(self):
        """Enchaîne une position droite + bras à zéro + expression joueur (animation festive)."""
        self.marty.stand_straight(300)
        self.marty.arms(0, 0, 300, False)
        self.set_expression("XDN")

    def marcher(self, direction: str, count: int = 1) -> None:
        """Fait avancer/reculer/pivoter le robot de *count* pas.

        direction: 'U' avant, 'B' arrière, 'L' gauche, 'R' droite
        """
        if not self._connexion.is_connected():
            return
        marty = self._connexion.marty
        for _ in range(count):
            if direction == 'U':
                marty.walk(1, step_length=STEP_LENGTH, move_time=STEP_TIME_MS)
            elif direction == 'B':
                marty.walk(1, step_length=-STEP_LENGTH, move_time=STEP_TIME_MS)
            elif direction == 'L':
                marty.sidestep('left', step_length=SIDE_STEP_LENGTH, move_time=SIDE_STEP_TIME)
            elif direction == 'R':
                marty.sidestep('right', step_length=SIDE_STEP_LENGTH, move_time=SIDE_STEP_TIME)


    def set_bras(self, tokens: list) -> None:
        """Positionne les bras selon les tokens reçus.

        tokens: liste parmi 'ALU', 'ALB', 'ARU', 'ARB'
        """
        if not self._connexion.is_connected():
            return
        marty = self._connexion.marty

        if len(tokens) == 2:
            marty.set_blocking(False)

        if 'ALU' in tokens:
            marty.move_joint(JOINT_LEFT_ARM, ARM_UP, STEP_TIME_MS)
        elif 'ALB' in tokens:
            marty.move_joint(JOINT_LEFT_ARM, ARM_BACK, STEP_TIME_MS)
        if 'ARU' in tokens:
            marty.move_joint(JOINT_RIGHT_ARM, ARM_UP, STEP_TIME_MS)
        elif 'ARB' in tokens:
            marty.move_joint(JOINT_RIGHT_ARM, ARM_BACK, STEP_TIME_MS)


    def set_expression(self, token: str) -> None:
        """Applique une expression au robot : yeux + LEDs selon le token reçu.

        tokens: 'XNT' neutre, 'XHP' content, 'XSD' triste, 'XNG' en colère, 'XDN' joueur
        """
        if not self._connexion.is_connected():
            return
        
        couleurs = [
            "red",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
            "white"
        ]
        marty = self._connexion.marty

        expressions = {
            "XNT": {
                "eyes": "normal",
                "color": "off"
            },
            "XHP": {
                "eyes": "excited",
                "color": "green"
            },
            "XSD": {
                "eyes": "wide",
                "color": "blue"
            },
            "XNG": {
                "eyes": "angry",
                "color": "red"
            },
            "XDN": {
                "eyes": "wiggle",
                "color": "rainbow_animation"
            },
            "67": {
                "eyes": "wiggle",
                "color": "67676767"
            },
        }

        if token not in expressions:
            return

        config = expressions[token]
        marty.set_blocking(False)
        if token in ["XSD","XNG","XHP"] :
            marty.disco_color(config["color"], marty.Disco.ALL, "all")
            marty.eyes(config["eyes"], move_time=500)

        elif token == "XNT" :
            marty.disco_off(api='led')
            marty.eyes(config["eyes"], move_time=300)
      
        elif token == "XDN" :
            marty.eyes(config["eyes"], move_time=1000)
            for _ in range(2):
                for couleur in couleurs:
                   marty.disco_color(couleur, marty.Disco.ALL, "all")
            marty.disco_off(api='led')

        elif token == "67" :
            marty.eyes(config["eyes"], move_time=1000)
            for _ in range(4):
                self.set_bras("ARU", "ALB")
                self.set_bras("ARB", "ALU")
            marty.disco_off(api='led')

    def reset_position(self) -> None:
        """Remet les bras et les yeux en position neutre."""
        if not self._connexion.is_connected():
            return
        marty = self._connexion.marty
        marty.set_blocking(False)
        marty.move_joint(JOINT_LEFT_ARM, 0, STEP_TIME_MS)
        marty.move_joint(JOINT_RIGHT_ARM, 0, STEP_TIME_MS)
        marty.disco_off(api='led')
        marty.eyes("normal", move_time=300)

    # ------------------------------------------------------------------
    # Capteurs
    # ------------------------------------------------------------------

    def get_couleur_raw(self) -> tuple:
        """Retourne (r, g, b) lus par le capteur de couleur, ou (0,0,0) si déconnecté."""
        if not self._connexion.is_connected():
            return (0, 0, 0)
        marty = self._connexion.marty
        r = marty.get_color_sensor_value_by_channel(0)
        g = marty.get_color_sensor_value_by_channel(1)
        b = marty.get_color_sensor_value_by_channel(2)
        return (r, g, b)
    
    def get_couleur(self):
        """Lit le capteur couleur et retourne le nom de la couleur calibrée la plus proche."""
        return self._calibrateur.get_couleur()
    
    def get_batterie(self) -> float:
        """Retourne le pourcentage de batterie restant, ou -1 si déconnecté."""
        if not self._connexion.is_connected():
            return -1
        return self._connexion.marty.get_battery_remaining()
