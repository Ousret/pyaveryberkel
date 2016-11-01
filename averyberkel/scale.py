import socket

class Scale(object):

    def __init__(self, uneAdresseIP, unPortTCP=3001, unTimeOutMaximum=5):
        self._ip = uneAdresseIP
        self._port = unPortTCP
        self._timeout = unTimeOutMaximum
        self._name = None

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @property
    def name(self):
        """
        Retourne les caractéristiques de la balance
        :return: str|None
        """
        return self._name

    @property
    def ip(self):
        """
        Récupère l'adresse IP de la balance
        :return: str
        """
        return self._ip

    @property
    def port(self):
        """
        Récupère le numéro de port utilisé
        :return: int
        """
        return self._port

    @property
    def timeout(self):
        """
        Récupère le délai de timeout (attente de la réponse balance)
        :return:
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """
        Change le délai de timeout (attente de la réponse balance)
        :param value:
        :return:
        """
        self._timeout = value
        if self._socket is not None:
            self._socket.settimeout(self.timeout)

    def ouvrir(self):
        """
        Ouvre le socket TCP
        :return: bool
        """
        try:
            self._socket.connect((self.ip, self.port))
            self._socket.settimeout(self.timeout)
            return True
        except socket.error as e:
            print(format(e))
            return False

    def fermer(self):
        """
        Ferme la connexion si elle n'est pas déjà fermé
        :return: bool
        """
        if self._socket is not None:
            self._socket.close()
            self._socket = None
            self._name = None
            return True

        return False

    def _envoyer(self, paquet):
        """
        Envoyer des données sur la connexion socket balance
        :param paquet:
        :return: bool
        """
        if self._socket is not None:

            try:
                self._socket.sendall(paquet)
            except Exception as e:
                print(format(e))
                return False

            return True
        return False

    def _recevoir(self):
        """
        Essaie de récupèrer un paquet si disponible
        :return: bytes|None
        """
        try:
            buf = self._socket.recv(1024)
            return buf
        except Exception as e:
            print(format(e))
            return None