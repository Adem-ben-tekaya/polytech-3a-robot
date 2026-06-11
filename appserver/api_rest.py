from flask import Flask, request, jsonify
"""
L'application arbitre utilise Flask pour exposer une API REST accessible aux applications joueur. 
Le joueur n'ouvre pas de port : il envoie seulement des requêtes. 
Le serveur, lui, écoute sur le port choisi, donc on ajoute temporairement 
une règle pare-feu limitée au réseau privé local.
"""
from gestion_battle import (
    lister_robots,
    afficher_reception,
    afficher_reception,
    afficher_scores,
    calculer_points,
    mettre_a_jour_classement
)
import uuid
import logging
from PyQt6.QtCore import QThread
from signaux import signals


app = Flask(__name__)
app.logger.disabled = True          #Désactive les logs Flask pour ne pas polluer la console
logging.getLogger('werkzeug').setLevel(logging.ERROR)


@app.route('/', methods=['GET'])
def ping():
    """
    Vérifie que le serveur est disponible 
    et renvoie simplement le numéro de version
    """
    print("Ping reçu")
    return jsonify({'version': '1.67'}), 200


@app.route('/hello', methods=['POST'])
def enregistrer_robot():   
    """
    Enregistre un nouveau robot et 
    lui attribue un identifiant unique et 
    renvoie cet identifiant au robot
    """
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
    """
    Donne la possiblilité à un robot de se donner un 
    nom personnalisé
    """
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
def demarrer_choregraphie():
    """
    Le robot annonce qu'il commence sa chorégraphie et 
    on lui répond avec le nombre de mouvements qu'il doit effectuer
    """
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
def recevoir_pas():
    """
    Le robot envoie les infos d'un pas effectué et 
    on calcule les points, on met à jour le score, 
    on renvoie les points obtenus
    """
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
def obtenir_score():
    """
    Renvoie le score total d'un robot
    """
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
    """
    Thread PyQt permettant d'exécuter le serveur Flask sans bloquer l'interface graphique.

    Cette classe encapsule le serveur WSGI Werkzeug utilisé par Flask.
    Elle démarre le serveur REST sur toutes les interfaces réseau de la machine
    grâce à l'adresse '0.0.0.0'.

    Attributs :
        port (int) :
            Port TCP sur lequel le serveur Flask doit écouter.
            Exemple : 8080.

        _server :
            Instance du serveur Werkzeug créée avec make_server.
            Vaut None tant que le serveur n'a pas encore été lancé.
    """

    def __init__(self, port: int):
        """
        Initialise le thread Flask.

        Paramètres :
            port (int) :
                Numéro du port sur lequel le serveur Flask sera lancé.

        Effets :
            - initialise le QThread ;
            - mémorise le port demandé ;
            - prépare l'attribut _server, qui contiendra plus tard le serveur Werkzeug.
        """
        super().__init__()
        self.port = port
        self._server = None

    def run(self):
        """
        Lance le serveur Flask dans le thread.

        Cette méthode est automatiquement exécutée lorsque start() est appelé
        sur l'objet FlaskThread.

        Effets :
            - crée un serveur Werkzeug associé à l'application Flask ;
            - écoute sur l'adresse '0.0.0.0' afin d'être accessible depuis le réseau ;
            - émet le signal serveur_demarre avec le port utilisé ;
            - bloque ce thread avec serve_forever(), sans bloquer l'interface PyQt.

        Précondition :
            - l'application Flask app doit être définie ;
            - le port doit être disponible.

        Postcondition :
            - le serveur REST est lancé et accepte les requêtes HTTP.

        Exceptions possibles :
            - erreur si le port est déjà utilisé ;
            - erreur si le pare-feu ou le système empêche l'ouverture du port.
        """
        from werkzeug.serving import make_server
        self._server = make_server('0.0.0.0', self.port, app)
        signals.serveur_demarre.emit(self.port)     
        self._server.serve_forever()

    def closeEvent(self, event):
        try:
            if self.flask_thread is not None and self.flask_thread.isRunning():
                print("Arrêt du serveur Flask...")
                self.flask_thread.stop()
                self.flask_thread.wait(3000)
                print("Serveur Flask arrêté.")
        except Exception as e:
            print(f"Erreur arrêt serveur : {e}")

        event.accept()

    def stop(self):
        """
        Arrête proprement le serveur Flask.

        Effets :
            - si le serveur Werkzeug existe, appelle shutdown() pour arrêter l'écoute HTTP ;
            - émet le signal serveur_arrete pour prévenir l'interface graphique.

        Précondition :
            - le serveur peut avoir été lancé ou non.

        Postcondition :
            - si le serveur était actif, il est arrêté ;
            - l'interface est informée de l'arrêt du serveur.

        Remarque :
            Cette méthode peut être appelée depuis l'interface PyQt, par exemple
            lorsqu'un bouton "Arrêter serveur" est pressé ou lors de la fermeture
            de l'application arbitre.
        """
        if self._server:
            self._server.shutdown()
        signals.serveur_arrete.emit()