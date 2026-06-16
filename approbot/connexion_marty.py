import threading
import urllib.request
import json

# Timeout (secondes) par hôte lors du scan réseau
_SCAN_TIMEOUT = 0.5 #Anciennement 1.5
# Nombre maximum de threads parallèles lors du scan
_MAX_THREADS = 64


class ConnexionMarty:
    """
    Gère la connexion à un robot Marty via martypy (Wi-Fi).
    """

    def __init__(self):
        self._marty = None
        self._connecte = False
        self._ip = None

    def connecter(self, ip: str) -> None:
        """
        Connecte le robot Marty à l'adresse *ip*.  
        Lève une exception en cas d'échec.
        """
        from martypy import Marty

        marty = Marty('wifi', ip, blocking=True)
        self._marty = marty
        self._connecte = True
        self._ip = ip

    def deconnecter(self) -> None:
        """
        Déconnecte le robot proprement.
        """
        if self._marty is None:
            return
        try:
            self._marty.stop('clear')
            self._marty.close()
        except Exception:
            pass

        self._marty = None
        self._connecte = False
        self._ip = None

    def is_connected(self) -> bool:
        return self._connecte

    @property
    def marty(self):
        """
        Accès direct à l'objet martypy (None si déconnecté).
        """
        return self._marty

    @staticmethod
    def nettoyer_adresse_reseau(adresse):
        """
        Permet une souplesse de l'entrée utilisateur pour l'ip du réseau.
        Vérifie la validité de l'adresse.

        Exs:
         - 192.168.0
         - 192.168.0.0
         - 192.168.0.0/24
        """
        adresse = adresse.strip()

        if "/" in adresse:
            adresse = adresse.split("/")[0]

        morceaux = adresse.split(".")

        if len(morceaux) not in (3, 4):
            return None
        try :
            if not all(0 <= int(octet) <= 255 for octet in morceaux):
                return None
        except ValueError:
            return None
        
        return ".".join(str(int(octet)) for octet in morceaux[:3])

    @staticmethod
    def nettoyer_adresse_marty(adresse):
        """
        Vérifie la validité de l'adresse.

        Exs:
         - 192.168.0.01 -> 192.168.0.1
         - 192.168.0.0111 -> Error
        """

        morceaux = adresse.split(".")

        if len(morceaux) != 4:
            return None
        try :
            if not all(0 <= int(octet) <= 255 for octet in morceaux):
                return None
        except ValueError:
            return None
        
        return ".".join(str(int(octet)) for octet in morceaux[:4])



    def rechercher_martys(self, reseau: str, debut: int = 1, fin: int = 254) -> list:
        """
        Recherche les Marty disponibles sur le réseau local.

        La fonction teste toutes les IP de reseau.1 à reseau.254.
        Chaque IP est testée dans un thread pour accélérer la recherche.
        Les serveurs trouvés sont ajoutés dans la liste PyQt.
        Un lock est utilisé pour éviter les conflits quand plusieurs threads trouvent un Marty en même temps.
        """
        resultats = []
        lock = threading.Lock()
        def sonder(i):
            ip = f"{reseau}.{i}"

            resultat_marty = self._sonder_http(ip)

            if resultat_marty is not None:
                with lock:
                    resultats.append(resultat_marty)

        threads = []

        for i in range(debut, fin + 1):
            t = threading.Thread(target=sonder, args=(i,), daemon=True)
            threads.append(t)
            t.start()

            while sum(1 for th in threads if th.is_alive()) >= _MAX_THREADS:
                pass

        for t in threads:
            t.join()

        return resultats

    @staticmethod
    def _sonder_http(ip: str):
        """
        Tente de détecter un Marty et de récupérer son friendlyName.

        Retourne :
        {
            "type": "marty",
            "nom": "NOM_DU_MARTY",
            "ip": "192.168.0.103"
        }

        ou None si ce n'est pas un Marty.
        """

        url = f"http://{ip}/api/friendlyname"

        try:
            req = urllib.request.Request(url)
            req.add_header("Connection", "close")

            with urllib.request.urlopen(req, timeout=_SCAN_TIMEOUT) as resp:
                code = resp.getcode()
                content = resp.read(512).decode("utf-8", errors="ignore").strip()

                if code != 200:
                    return None

                data = json.loads(content)

                if data.get("rslt") == "ok":
                    friendly_name = data.get("friendlyName", ip)

                    return {
                        "type": "marty",
                        "nom": f"{friendly_name}",
                        "ip": ip
                    }

        except Exception:
            return None

        return None