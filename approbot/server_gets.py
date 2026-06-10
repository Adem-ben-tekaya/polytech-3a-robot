import requests

MARTY_NAME = "MATHILDE PANOT"
IP_SERVEUR = "10.170.49.21" #TODO

class RequetesServeur:
    def __init__(self):
        self.url_serveur = None
        self.rid = None

    def definir_url(self):
        ip_server= IP_SERVEUR #TODO
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
        reponse = requests.post(f"{self.url_serveur}/hello",timeout=3)
        reponse.raise_for_status()
        try:
            return reponse.json()
        except Exception:
            return reponse.text
        
    def nom_robot(self, rid, nom):
        self._check_url()
        reponse = requests.post(f"{self.url_serveur}/name",json={"rid": rid,"name": nom},timeout=3)
        reponse.raise_for_status()
        return reponse.json()

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
        return int(reponse.text)

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

        return int(reponse.text)

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

        return int(reponse.text)

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

        reponse = requests.post(
            f"{self.url_serveur}/bye",
            json=donnees,
            timeout=3
        )
        reponse.raise_for_status()

        self.rid = None

    def set_name(self):
        """
        Definir un nom pour le robot
        """
        self._check_url()
        self._check_rid()

        donnees = {
            "rid": self.rid,
            "name": MARTY_NAME
        }

        reponse = requests.post(
            f"{self.url_serveur}/name",
            json=donnees,
            timeout=3
        )
        reponse.raise_for_status()

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


    def est_enregistre(self):
        return self.rid is not None

    def _check_url(self):
        if self.url_serveur is None:
            raise RuntimeError("URL du serveur non définie")

    def _check_rid(self):
        if self.rid is None:
            raise RuntimeError("Robot non enregistré. Il faut appeler hello() avant.")
        
if __name__ == "__main__":
    serveur = RequetesServeur()

    serveur.definir_url()

    version = serveur.verifier_connexion()
    print("Version serveur :", version)

    rid = serveur.hello()
    print("Robot enregistré avec rid :", rid)

    serveur.set_name()
    print("Le robot s'appelle maintenant : ", MARTY_NAME)

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