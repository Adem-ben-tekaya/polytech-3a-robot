from flask import Flask, request, jsonify
from gestion_battle import *
import uuid
import logging
from PyQt6.QtCore import QThread
from signaux import signals


app = Flask(__name__)
app.logger.disabled = True          # Désactive les logs Flask pour ne pas polluer la console
logging.getLogger('werkzeug').setLevel(logging.ERROR)


@app.route('/', methods=['GET'])
def ping():         #Vérifie que le serveur est disponible et renvoie simplement le numéro de version
    print("Ping reçu")
    return jsonify({'version': '1.2'}), 200


@app.route('/hello', methods=['POST'])
def enregistrer_robot():            #Enregistre un nouveau robot et lui attribue un identifiant unique et renvoie cet identifiant au robot
    nouvel_identifiant = uuid.uuid4().hex[:6].upper()
    ip_robot = request.remote_addr
    robots_connus.append([nouvel_identifiant, ip_robot, 0])
    print(f"Nouveau robot enregistré : {nouvel_identifiant}")
    lister_robots()
    signals.robot_enregistre.emit(nouvel_identifiant)   
    signals.score_mis_a_jour.emit()
    return jsonify({'rid': nouvel_identifiant}), 200


@app.route('/name', methods=['POST'])
def recevoir_nom_robot():
    donnees = request.json
    identifiant_robot = donnees.get('rid')
    nom_robot = donnees.get('name')
    if not nom_robot:
        return jsonify({'error': 'Nom invalide'}), 400
    for robot in robots_connus:
        if robot[0] == identifiant_robot:
            robot[1] = nom_robot
            signals.score_mis_a_jour.emit()
            return jsonify({}), 200
    return jsonify({'error': 'Robot inconnu'}), 404


@app.route('/start', methods=['POST'])
def demarrer_choregraphie():            #Le robot annonce qu'il commence sa chorégraphie et on lui répond avec le nombre de mouvements qu'il doit effectuer
    donnees = request.json          #Lit automatiquement le corps JSON de la requête
    identifiant_robot = donnees.get('rid')
    robot_trouve = None
    for info in robots_connus:
        if info[0] == identifiant_robot:
            robot_trouve = info
    if robot_trouve is None:
        return jsonify({'error': 'Robot inconnu'}), 404
    nombre_mouvements = regles_battle.get('MVS', 10)            #Le nombre de mouvements vient du fichier .battle, sinon 10 par défaut
    print(f"Robot = {identifiant_robot} démarre, {nombre_mouvements} mouvements")
    return jsonify({'steps': nombre_mouvements}), 200


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
        return jsonify({'error': 'Robot inconnu'}), 404
    points = calculer_points(couleur, bras, exp)
    robot_trouve[2] = robot_trouve[2] + points
    afficher_reception(couleur, bras, exp, points)
    signals.pas_recu.emit(identifiant_robot, couleur, bras, exp, points)    
    signals.score_mis_a_jour.emit()
    return jsonify({'points': points}), 200


@app.route('/score', methods=['GET'])
def obtenir_score():            #Renvoie le score total d'un robot
    identifiant_robot = request.args.get('rid')             #Lit les paramètres dans l'URL
    robot_trouve = None
    for info in robots_connus:
        if info[0] == identifiant_robot:
            robot_trouve = info
    if robot_trouve is None:
        return jsonify({'error': 'Robot inconnu'}), 404
    score = robot_trouve[2]
    print(f"Robot = {identifiant_robot}, score = {score}")
    afficher_scores()
    return jsonify({'points': score}), 200


@app.route('/bye', methods=['POST'])
def deconnecter_robot():
    """
    Lorsque le robot se déconnecte,
    on affiche son score final
    et on le retire de la liste
    """
    data = request.json or {}
    rid = data.get('rid')

    if not rid:
        return jsonify({'error': 'rid manquant'}), 400
    
    robot_trouve = None

    for info in robots_connus:
        if info[0] == rid:
            robot_trouve = info
            break
    

    if robot_trouve is None:
        return jsonify({'error': 'Robot inconnu'}), 404
    
    print(f"Robot = {rid} se déconnecte. Score final = {robot_trouve[2]}")

    mettre_a_jour_classement(robot_trouve[1], robot_trouve[2])
    robots_connus.remove(robot_trouve)

    afficher_scores()

    signals.robot_deconnecte.emit(rid)    
    signals.score_mis_a_jour.emit()

    return jsonify({"status": "ok"}), 200


class FlaskThread(QThread):

    def __init__(self, port: int):
        super().__init__()
        self.port = port
        self._server = None

    def run(self):
        from werkzeug.serving import make_server
        self._server = make_server('0.0.0.0', self.port, app)
        signals.serveur_demarre.emit(self.port)     
        self._server.serve_forever()

    def stop(self):
        if self._server:
            self._server.shutdown()
        signals.serveur_arrete.emit()