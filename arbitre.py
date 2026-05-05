robots_connus = []

def lister_robots():
    if not robots_connus:
        print("Aucun robot enregistré !")
        exit
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
    else:
        classement = sorted(robots_connus, key=lambda x: x[2], reverse=True)    #Tri par score décroissant
        i=1
        for info in classement:
            print(f" #{i}, ID : {info[0]}, Nom : {info[1]}, Score : {info[2]}")
            i=i+1
