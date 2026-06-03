import socket
import threading
import urllib.request
import urllib.error


# Mots-clés recherchés dans la réponse HTTP pour identifier un Marty
_MARTY_KEYWORDS = ('marty', 'ric', 'robotical')
# Timeout (secondes) par hôte lors du scan réseau
_SCAN_TIMEOUT = 1.5
# Nombre maximum de threads parallèles lors du scan
_MAX_THREADS = 64


class ConnexionMarty:
    """Gère la connexion à un robot Marty via martypy (Wi-Fi)."""

    def __init__(self):
        self._marty = None
        self._connecte = False
        self._ip = None

    def connecter(self, ip: str) -> None:
        """Connecte le robot Marty à l'adresse *ip*.  Lève une exception en cas d'échec."""
        from martypy import Marty

        marty = Marty('wifi', ip, blocking=True)
        self._marty = marty
        self._connecte = True
        self._ip = ip

    def deconnecter(self) -> None:
        """Déconnecte le robot proprement."""
        self._connecte = False
        self._ip = None
        if self._marty is None:
            return
        try:
            self._marty.stop('clear')
            self._marty.disconnect()
        except Exception:
            pass
        self._marty = None

    def is_connected(self) -> bool:
        return self._connecte

    @property
    def marty(self):
        """Accès direct à l'objet martypy (None si déconnecté)."""
        return self._marty

    def rechercher_martys(self, reseau: str = "192.168.1",
                          debut: int = 1, fin: int = 254) -> list:
        """
        Scanne les adresses {reseau}.{debut} … {reseau}.{fin} via HTTP.

        Retourne une liste de dicts : [{'nom': str, 'ip': str}, ...]
        Les robots dont la réponse HTTP contient un mot-clé Marty sont listés
        en premier (marqués '[Marty]'), les autres hôtes actifs sont ignorés.
        """
        resultats = []
        lock = threading.Lock()

        def sonder(i):
            ip = f"{reseau}.{i}"
            nom, est_marty = self._sonder_http(ip)
            if est_marty:
                with lock:
                    resultats.append({'nom': f'[Marty] {nom}', 'ip': ip})

        threads = []
        for i in range(debut, fin + 1):
            t = threading.Thread(target=sonder, args=(i,), daemon=True)
            threads.append(t)
            t.start()
            # Limite le nombre de threads actifs simultanément
            while sum(1 for th in threads if th.is_alive()) >= _MAX_THREADS:
                pass

        for t in threads:
            t.join()

        return resultats

    @staticmethod
    def _sonder_http(ip: str):
        """
        Tente un GET HTTP sur l'IP.

        Retourne (nom_affichage, est_marty).
        nom_affichage est '' si l'hôte est injoignable.
        """
        url = f'http://{ip}/'
        try:
            req = urllib.request.Request(url)
            req.add_header('Connection', 'close')
            with urllib.request.urlopen(req, timeout=_SCAN_TIMEOUT) as resp:
                server  = (resp.getheader('Server') or '').lower()
                content = resp.read(256).decode('utf-8', errors='ignore').lower()
                est_marty = any(
                    kw in server or kw in content for kw in _MARTY_KEYWORDS
                )
                nom = ConnexionMarty._hostname(ip)
                return nom, est_marty
        except urllib.error.HTTPError:
            # Le serveur répond (4xx/5xx) mais n'est probablement pas un Marty
            return ConnexionMarty._hostname(ip), False
        except Exception:
            return '', False

    @staticmethod
    def _hostname(ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except OSError:
            return ip
