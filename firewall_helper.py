import sys
import subprocess


def ajouter_regle(port):
    nom_regle = f"Marty Supreme Server {port}"

    commande = (
        f'netsh advfirewall firewall add rule '
        f'name="{nom_regle}" '
        f'dir=in '
        f'action=allow '
        f'protocol=TCP '
        f'localport={port} '
        f'profile=private '
        f'remoteip=localsubnet'
    )

    subprocess.run(commande, shell=True, check=True)
    print(f'firewall_helper : règle {nom_regle} ajoutée')


def supprimer_regle(port):
    nom_regle = f"Marty Supreme Server {port}"

    commande = (
        f'netsh advfirewall firewall delete rule '
        f'name="{nom_regle}"'
    )

    subprocess.run(commande, shell=True, check=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : dist/firewall_helper.exe add|delete PORT")
        sys.exit(1)

    action = sys.argv[1]
    port = int(sys.argv[2])

    if action == "add":
        ajouter_regle(port)

    elif action == "delete":
        supprimer_regle(port)

    else:
        print("Action inconnue")
        sys.exit(1)