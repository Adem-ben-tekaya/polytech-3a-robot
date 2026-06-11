import requests

class ServerGets:
    def __init__(self):
        self.url_serveur = None
        self.rid = None

    def definir_url(self,ip):
        ip_server= ip
        url_serveur = "http://"+ip_server+":8080"
        self.url_serveur = url_serveur.rstrip("/")

    def verifier_connexion(self):
        """
        GET /
        Renvoie la version du serveur.
        """
        self._check_url()

        reponse = requests.get(f"{self.url_serveur}/", timeout=3)
        reponse.raise_for_status()

        return reponse.text

    def hello(self):
        self._check_url()

        reponse = requests.post(
            f"{self.url_serveur}/hello",
            timeout=3
        )
        reponse.raise_for_status()

        try:
            data = reponse.json()
            if isinstance(data, dict):
                self.rid = data.get("rid")
            else:
                self.rid = str(data)

        except Exception:
            self.rid = reponse.text.strip()

        return data

    def start(self):
        self._check_url()
        self._check_rid()

        donnees = {
            "rid": self.rid
        }

        reponse = requests.post(
            f"{self.url_serveur}/start",
            json=donnees,
            timeout=3
        )

        print("Réponse start :", reponse.status_code, reponse.text)

        reponse.raise_for_status()

        try:
            data = reponse.json()

            if isinstance(data, dict):
                steps = int(data.get('steps'))

        except Exception as e:
            return f"Erreur donnees invalides {e}"
        
        return steps

    def step(self, couleur, bras, expression):
        """
        POST /step

        couleur : ex "G", "R", "B"
        bras : ex "ALU+ARU"
        expression : ex "XNT"

        Renvoie les points obtenus pour ce pas.
        """
        self._check_url()
        self._check_rid()

        donnees = {
            "rid": self.rid,
            "col": couleur,
            "arm": bras,
            "exp": expression
        }

        reponse = requests.post(
            f"{self.url_serveur}/step",
            json=donnees,
            timeout=3
        )
        reponse.raise_for_status()

        try:
            data = reponse.json()

            if isinstance(data, dict):
                points = int(data.get('points'))

        except Exception as e:
            return f"Erreur donnees invalides {e}"

        return points

    def score(self):
        """
        GET /score
        Envoie le rid.
        Renvoie le score total du robot.
        """
        self._check_url()
        self._check_rid()

        params = {
            "rid": self.rid
        }

        reponse = requests.get(
            f"{self.url_serveur}/score",
            params=params,
            timeout=3
        )
        reponse.raise_for_status()

        try:
            data = reponse.json()

            if isinstance(data, dict):
                points = int(data.get('points'))

        except Exception as e:
            return f"Erreur donnees invalides {e}"

        return points

    def bye(self):
        """
        POST /bye
        Déconnecte le robot du serveur.
        """
        self._check_url()
        self._check_rid()

        donnees = {
            "rid": self.rid
        }
        print("Envoi /bye avec :", donnees)

        reponse = requests.post(
            f"{self.url_serveur}/bye",
            json=donnees,
            timeout=3
        )
        print("Réponse /bye :", reponse.status_code, reponse.text)

        reponse.raise_for_status()

        self.rid = None

    def nom_robot(self, nom):
        self._check_url()
        self._check_rid()

        reponse = requests.post(
            f"{self.url_serveur}/name",
            json={"rid": self.rid, "name": nom},
            timeout=3
        )
        reponse.raise_for_status()
        return reponse.json()

    @staticmethod
    def sonder_serveur(ip: str, timeout=1):
        try:
            reponse = requests.get(f"http://{ip}:8080/",timeout=timeout)
            if reponse.status_code != 200:
                return None
            data = reponse.json()
            return {"type": "serveur","nom": f"Serveur REST v{data.get('version', '?')}","ip": ip}
        except Exception:
            return None
        
    def deconnecter(self):
        if not self.est_enregistre():
            print("Aucun rid enregistré, pas de /bye à envoyer.")
            return False

        try:
            self.bye()
            print("Requête /bye envoyée avec succès.")
            return True

        except Exception as e:
            print(f"Erreur pendant /bye : {e}")
            return False


    def est_enregistre(self):
        return self.rid is not None

    def _check_url(self):
        if self.url_serveur is None:
            raise RuntimeError("URL du serveur non définie")

    def _check_rid(self):
        if self.rid is None:
            raise RuntimeError("Robot non enregistré. Il faut appeler hello() avant.")
        
if __name__ == "__main__":
    serveur = ServerGets()

    serveur.definir_url("192.168.1.7")

    version = serveur.verifier_connexion()
    print("Version serveur :", version)

    rid = serveur.hello()
    print("Robot enregistré avec rid :", rid)

    robot = "GOATAGA"
    serveur.nom_robot(robot)
    print("Le robot s'appelle maintenant : ", robot)

    nb_pas = serveur.start()
    print("Nombre de pas :", nb_pas)

    points = serveur.step(
        couleur="G",
        bras="ALU+ARU",
        expression="XNT"
    )
    print("Points gagnés :", points)

    score = serveur.score()
    print("Score total :", score)

    serveur.bye()
    print("Robot déconnecté")