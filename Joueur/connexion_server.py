import requests


class ConnexionServeur:
    def __init__(self):
        self.url_serveur = None
        self.rid = None

    def definir_url(self):
        """
        Exemple :
        http://192.168.1.12:8000
        """
        ip_server= str(input("Entrez IP du serveur : "))
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
        """
        POST /hello
        Enregistre le robot côté serveur.
        Le serveur renvoie un identifiant robot.
        """
        self._check_url()

        reponse = requests.post(f"{self.url_serveur}/hello", timeout=3)
        reponse.raise_for_status()

        self.rid = reponse.text.strip()
        return self.rid

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
            data=donnees,
            timeout=3
        )
        reponse.raise_for_status()

        self.rid = None

    def est_enregistre(self):
        return self.rid is not None

    def _check_url(self):
        if self.url_serveur is None:
            raise RuntimeError("URL du serveur non définie")

    def _check_rid(self):
        if self.rid is None:
            raise RuntimeError("Robot non enregistré. Il faut appeler hello() avant.")
        
if __name__ == "__main__":
    serveur = ConnexionServeur()

    serveur.definir_url()

    version = serveur.verifier_connexion()
    print("Version serveur :", version)

    rid = serveur.hello()
    print("Robot enregistré avec rid :", rid)

    nb_pas = serveur.start()
    print("Nombre de pas :", nb_pas)

    points = serveur.step(
        couleur="G",
        bras="ALU+ARU",
        expression="XNT"
    )
    print("Points gagnés :", points)

    # score = serveur.score()
    # print("Score total :", score)

    # serveur.bye()
    # print("Robot déconnecté")