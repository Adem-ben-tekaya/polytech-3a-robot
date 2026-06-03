import requests 

SERVEUR = "http://localhost:8080"

#Enregistrement
rid = requests.post(f"{SERVEUR}/hello").text
print(f"Mon ID : {rid}")

#Démarrage
nb_mouvements = requests.post(f"{SERVEUR}/start", json={"rid": rid}).text
print(f"Je dois faire {nb_mouvements} mouvements")

#Quelques pas
pas = [{"col": "N", "arm": "ARU+ALB", "exp": "XNG"}, {"col": "B", "arm": "", "exp": "XSD"}, {"col": "R", "arm": "ALU+ARU", "exp": "XNG"},]
for p in pas:
    points = requests.post(f"{SERVEUR}/step", json={"rid": rid, **p}).text
    print(f"  pas joué => {points} points")

#Score final
score = requests.get(f"{SERVEUR}/score", params={"rid": rid}).text
print(f"Score total : {score}")

#Déconnexion
requests.post(f"{SERVEUR}/bye", json={"rid": rid})