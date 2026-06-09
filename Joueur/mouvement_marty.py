from Joueur.calibrateur_couleurs import CalibrateurCouleurs

JOINT_LEFT_ARM   = 6
JOINT_RIGHT_ARM  = 7
ARM_UP           = 100
ARM_BACK         = -100
STEP_LENGTH      = 40
STEP_TIME_MS     = 1500
SIDE_STEP_LENGTH = 100
SIDE_STEP_TIME   = 200


class MouvementMarty:

    def __init__(self, connexion, calibrateur):
        self._connexion = connexion
        self._calibrateur = calibrateur
        
    def goat_dance(self):
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

    # ------------------------------------------------------------------
    # Bras
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Expression
    # ------------------------------------------------------------------

    def set_expression(self, token: str) -> None:
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
            marty.eyes(config["eyes"], move_time=1000)
      
        elif token == "XDN" :
            marty.eyes(config["eyes"], move_time=1000)
            for _ in range(2):
                for couleur in couleurs:
                   marty.disco_color(couleur, marty.Disco.ALL, "all")
            marty.disco_off(api='led')

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
    
    def get_couleur(self, pied="left"):
        return self._calibrateur.detecter_couleur(pied)
    
    def get_batterie(self) -> float:
        """Retourne le pourcentage de batterie restant, ou -1 si déconnecté."""
        if not self._connexion.is_connected():
            return -1
        return self._connexion.marty.get_battery_remaining()
