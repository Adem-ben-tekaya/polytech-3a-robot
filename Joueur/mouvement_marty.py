from Joueur.calibrateur_couleurs import CalibrateurCouleurs

JOINT_LEFT_ARM   = 6
JOINT_RIGHT_ARM  = 7
ARM_UP           = 60
ARM_BACK         = -60
STEP_LENGTH      = 40
STEP_TIME_MS     = 1500
SIDE_STEP_LENGTH = 100
SIDE_STEP_TIME   = 1000


class MouvementMarty:
    """Commandes de mouvement pour un robot Marty connecté via ConnexionMarty."""

    def __init__(self, connexion):
        self._connexion = connexion

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
        """Applique une expression au visage du robot.

        token: 'XNT' neutre, 'XSD' triste, 'XNG' en colère, 'XHP' content, 'XDN' joueur
        """
        if not self._connexion.is_connected():
            return
        marty = self._connexion.marty
        expressions = {
            'XNT': ('normal',  (255, 255, 255)),
            'XSD': ('sad',     (0,   0,   255)),
            'XNG': ('angry',   (255, 0,   0)),
            'XHP': ('excited', (0,   255, 0)),
            'XDN': ('normal',  (255, 165, 0)),
        }
        if token not in expressions:
            return
        eyes_mode, (r, g, b) = expressions[token]
        marty.eyes(eyes_mode)
        marty.set_leds('eyes', r, g, b)

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
        return detecter_couleur(self)

    def get_batterie(self) -> float:
        """Retourne le pourcentage de batterie restant, ou -1 si déconnecté."""
        if not self._connexion.is_connected():
            return -1
        return self._connexion.marty.get_battery_remaining()
