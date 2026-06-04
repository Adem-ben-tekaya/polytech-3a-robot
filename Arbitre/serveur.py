from flask import Flask, request
from arbitre import *
import uuid
import argparse
import sys
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET'])
def ping():         #Vérifie que le serveur est disponible et renvoie simplement le numéro de version
    print("Ping reçu")
    return '1.2', 200


@app.route('/hello', methods=['POST'])
def enregistrer_robot():            #Enregistre un nouveau robot et lui attribue un identifiant unique et renvoie cet identifiant au robot
    nouvel_identifiant = uuid.uuid4().hex[:6].upper()             # On génère un identifiant unique de 6 caractères en majuscules
    robots_connus.append([nouvel_identifiant, nouvel_identifiant, 0])
    print(f"Nouveau robot enregistré : {nouvel_identifiant}")
    lister_robots()
    return nouvel_identifiant, 200


@app.route('/start', methods=['POST'])
def demarrer_choregraphie():            #Le robot annonce qu'il commence sa chorégraphie et on lui répond avec le nombre de mouvements qu'il doit effectuer
    donnees = request.json          #Lit automatiquement le corps JSON de la requête
    identifiant_robot = donnees.get('rid')
    robot_trouve = None
    for info in robots_connus:
        if info[0] == identifiant_robot:
            robot_trouve = info
    if robot_trouve is None:
        return 'Robot inconnu', 404
    nombre_mouvements = regles_battle.get('MVS', 10)            #Le nombre de mouvements vient du fichier .battle, sinon 10 par défaut
    print(f"Robot = {identifiant_robot} démarre, {nombre_mouvements} mouvements")
    return str(nombre_mouvements), 200


@app.route('/step', methods=['POST'])
def recevoir_pas():         #Le robot envoie les infos d'un pas effectué et on calcule les points, on met à jour le score, on renvoie les points obtenus
    donnees = request.json
    identifiant_robot = donnees.get('rid')
    couleur = donnees.get('col', '')
    bras = donnees.get('arm', '')
    exp = donnees.get('exp', '')
    robot_trouve = None
    for info in robots_connus:
        if info[0] == identifiant_robot:
            robot_trouve = info
    if robot_trouve is None:
        return 'Robot inconnu', 404
    points = calculer_points(couleur, bras, exp)
    robot_trouve[2] = robot_trouve[2] + points
    afficher_reception(couleur, bras, exp, points)
    return str(points), 200


@app.route('/score', methods=['GET'])
def obtenir_score():            #Renvoie le score total d'un robot
    identifiant_robot = request.args.get('rid')             #Lit les paramètres dans l'URL
    robot_trouve = None
    for info in robots_connus:
        if info[0] == identifiant_robot:
            robot_trouve = info
    if robot_trouve is None:
        return 'Robot inconnu', 404
    score = robot_trouve[2]
    print(f"Robot = {identifiant_robot}, score = {score}")
    afficher_scores()  
    return str(score), 200


@app.route('/bye', methods=['POST'])
def deconnecter_robot():            #Le robot se déconnecte et on affiche son score final et on le retire de la liste
    donnees = request.json
    identifiant_robot = donnees.get('rid')
    robot_trouve = None
    for info in robots_connus:
        if info[0] == identifiant_robot:
            robot_trouve = info
    if robot_trouve is None:
        return 'Robot inconnu', 404
    print(f"Robot = {identifiant_robot} se déconnecte. Score final = {robot_trouve[2]}")
    afficher_scores()                   
    robots_connus.remove(robot_trouve)  
    return '', 200


def main():
    subprocess.run('netsh advfirewall firewall add rule name="Flask 8080" dir=in action=allow protocol=TCP localport=8080', shell=True)
    #Lecture des arguments de la ligne de commande
    parser = argparse.ArgumentParser(description='Serveur Arbitre - Dance Battle')
    parser.add_argument('--battle', type=str, default=None, help='Chemin vers le fichier .battle à charger au démarrage')
    parser.add_argument('--port', type=int, default=8080, help="Port d'écoute du serveur HTTP")
    args = parser.parse_args()

    if args.battle:
        print(f"\nChargement du fichier .battle : {args.battle}")
        charger_battle(args.battle)
    else:
        print("\nAucun fichier .battle fourni. Les scores seront toujours 0.")

    print(f"Serveur démarré sur le port {args.port}")

    try:
        app.run(host='0.0.0.0', port=args.port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
        subprocess.run('netsh advfirewall firewall delete rule name="Flask 8080"', shell=True)
        afficher_scores()
        sys.exit(0)
    

if __name__ == '__main__':
    main()
