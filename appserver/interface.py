import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication
from arbitre import charger_battle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.style import STYLE
from ui.fenetre import FenetrePrincipale


def main():
    parser = argparse.ArgumentParser(description='Dance Battle — Interface serveur arbitre')
    parser.add_argument('--battle', type=str, default=None, help='Chemin vers un fichier .battle à charger au démarrage')
    parser.add_argument('--port', type=int, default=8080, help="Port d'écoute du serveur HTTP (défaut : 8080)")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    fenetre = FenetrePrincipale()
    if args.port != 8080:
        fenetre.spin_port.setText(str(args.port))
    if args.battle:
        charger_battle(args.battle)
        fenetre.battle_charge = True
        fenetre.lbl_battle_info.setText(f"{args.battle.split('/')[-1]}")
        fenetre._log(f"Fichier chargé au démarrage : {args.battle}", "#f39c12")
        fenetre.maj_status()
    fenetre.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
