import json
import os

robots_connus = []
regles_battle = {}

DOSSIER_ACTUEL = os.path.dirname(os.path.abspath(__file__))
FICHIER_CLASSEMENT = os.path.join(DOSSIER_ACTUEL, "classement.json")


def lister_robots():
    if not robots_connus:
        print("Aucun robot enregistré !")
    else:
        print("Robots connus :")
        for info in robots_connus:
            print(f"ID : {info[0]}, Nom : {info[1]}, Score :  {info[2]}")


def afficher_reception(couleur, bras, exp, points):
    print(f"Case : {couleur}, bras : {bras}, expression : {exp} et points : {points}")


def afficher_scores():
    print("Scores :")

    if not robots_connus:
        print("Aucun robot enregistré !")
        return
    
    classement = sorted(
        robots_connus, 
        key=lambda x: x[2], 
        reverse=True #Tri par score décroissant
        )
    
    for i,info in enumerate(classement,start=1):
        print(f" #{i}, ID : {info[0]}, Nom : {info[1]}, Score : {info[2]}")


def charger_battle(chemin_fichier):

    global regles_battle    #Pour modifier regles_battle en dehors de la fonction
    regles_battle = {}
    couleur = None

    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            for ligne in f:
                ligne = ligne.strip()

                if not ligne:
                    continue

                if ligne.startswith('MVS'):
                    parties = ligne.split()
                    regles_battle['MVS'] = int(parties[1])
                    print(f" Nombre de mouvements : {regles_battle['MVS']}")
                    continue

                if ligne.startswith('[') and ligne.endswith(']'):
                    couleur = ligne[1:-1]
                    regles_battle[couleur] = []
                    print(f"Couleur '{couleur}' chargée")
                    continue

                if '=' in ligne and couleur is not None:
                    gauche, droite = ligne.split('=')
                    points = int(droite)

                    if '+' in gauche:
                        tokens = gauche.split('+')
                        regle = {'type': 'ET', 'tokens': tokens, 'points': points}

                    elif ',' in gauche:
                        tokens = gauche.split(',')
                        regle = {'type': 'OU', 'tokens': tokens, 'points': points}

                    else:
                        regle = {'type': 'SEUL', 'tokens': [gauche], 'points': points}

                    regles_battle[couleur].append(regle)
                    continue

        print("Fichier chargé avec succès.")

    except FileNotFoundError:
        print("Fichier .battle introuvable.")
    except Exception as e:
        print(f"Impossible de lire le fichier .battle : {e}")


def calculer_points(couleur, bras, exp):

    if not regles_battle:
        return 0
    if couleur not in regles_battle:
        return 0

    ce_que_le_robot_a_fait = [exp]
    if bras != '':
        for mouvement in bras.split('+'):
            ce_que_le_robot_a_fait.append(mouvement.strip())

    total = 0

    for regle in regles_battle[couleur]:
        tokens_regle = regle['tokens']
        pts = regle['points']

        if regle['type'] == 'ET':
            tous_presents = True
            for token in tokens_regle:
                if token not in ce_que_le_robot_a_fait:
                    tous_presents = False
            if tous_presents:
                total += pts

        elif regle['type'] == 'OU':
            au_moins_un_present = False
            for token in tokens_regle:
                if token in ce_que_le_robot_a_fait:
                    au_moins_un_present = True
            if au_moins_un_present:
                total += pts

        elif regle['type'] == 'SEUL':
            if tokens_regle[0] in ce_que_le_robot_a_fait:
                total += pts

    return total


def charger_classement():
    if not os.path.exists(FICHIER_CLASSEMENT):
        return []
    try:
        with open(FICHIER_CLASSEMENT, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def sauvegarder_classement(classement):
    with open(FICHIER_CLASSEMENT, "w", encoding="utf-8") as f:
        json.dump(classement, f, indent=4, ensure_ascii=False)

def mettre_a_jour_classement(nom, score):
    classement = charger_classement()
    classement.append({"nom": nom, "score": score})
    classement.sort(key=lambda x: x["score"], reverse=True)
    classement = classement[:10]
    sauvegarder_classement(classement)
