from averyberkel.scale import Scale
from hexdump import hexdump

# Ce que l'on sait :
TAILLE_EN_TETES = 0x33

COMMANDE_CREATION = 0xd55
COMMANDE_SUPPRESSION = 0xd43
COMMANDE_LECTURE_PLU = 0xd44
COMMANDE_DEMANDE_HELLO = 0x3b51
COMMANDE_NET = 0x1f51

# Une petite idée..
CLIENT_UNKNOWN_CONSTANT = bytes.fromhex('63')
BALANCE_UNKNOWN_CONSTANT_XW = bytes.fromhex('ff')
BALANCE_UNKNOWN_CONSTANT_R = bytes.fromhex('fe')

# Aucune idée :
COMMANDE_CREATION_MAGIC_0 = bytes.fromhex('000000000000000000000000001c20')
COMMANDE_CREATION_FORMAT = bytes.fromhex('2049')

CONSTANTE_UNKNOWN_0 = bytes.fromhex('000001014e7fff')
CONSTANTE_UNKNOWN_1 = bytes.fromhex('00005af1')


class CannotConstructPayloadException(Exception):
    pass


class WrongHeadersSizeException(Exception):
    pass


class UnableInatializeScaleException(Exception):
    pass


class MX(Scale):
    def __init__(self, uneAdresseIP, unIdentifiantBalance=1):
        super().__init__(uneAdresseIP, 3001)

        self._balance_id = unIdentifiantBalance.to_bytes(4, byteorder='big')
        self._packet_id = 0xf316

    @property
    def packet_id(self):
        """
        Donne un identifiant de conversation. Auto increment à chaque appel.
        :return: int
        """
        self._packet_id += 1
        return self._packet_id

    @property
    def balance_id(self):
        """
        Retourne l'identifiant de balance actuel
        :return: bytes
        """
        return self._balance_id

    def ouvrir(self):
        if super().ouvrir() is True:

            if self._initialiser() is False:
                self.fermer()
                raise UnableInatializeScaleException('Impossible d\'initialiser la balance %s:%i' % (self.ip, self.port))

            return True

        return False

    def _recuperer_reponse(self):
        """
        Décode une réponse de la balance si existant
        :return: MagicMethod ID, Identifiant Méthode, Numéro de conversation, Données(Payload)
        """
        buf = self._recevoir()

        if buf is None:
            return None

        if len(buf) < TAILLE_EN_TETES:
            raise WrongHeadersSizeException('Le message est imcompréhensible, la taille des en-tetes est mauvaise.')

        magic_method = buf[0x24:0x26]
        identifiant_methode = buf[0x26:0x2A]
        packet_id = buf[0x31:0x33]

        if len(buf) > TAILLE_EN_TETES:
            data = buf[0x33:-1]
        else:
            data = None

        return (int.from_bytes(magic_method, byteorder='big'), int.from_bytes(identifiant_methode, byteorder='big'), int.from_bytes(packet_id, byteorder='big'), data)

    def _convertir_texte(self, unTexte):
        """
        Convertir un texte vers bytes ASCII pour que la balance le comprenne.
        :param unTexte: Le texte cible
        :return: bytes
        """
        return bytes(unTexte, 'ascii', 'ignore') + bytes([0xa, 0x0])

    def _construire_args(self, *args):
        """
        Construire le 'payload' d'arguments pour la balance
        :param args: La liste des arguments
        :return: bytes
        """
        res = bytes()
        i = 0
        for element in args:
            i += 1
            if not isinstance(element, bytes):
                raise CannotConstructPayloadException('Impossible de compacter la liste d\'arguments, les paramètres doivent être des "bytes".')
            res += element

        return res

    def _construire_paquet(self, unIdentifiantCommande, unPaquetArguments, magic_method=0x2049, magic_0=0x1c20, balance_target=BALANCE_UNKNOWN_CONSTANT_XW):
        """
        Construit un paquet en essyant d'imiter le protocol MX AveryBerkel
        :param unIdentifiantCommande: Le numéro de commande
        :param unPaquetArguments: Le tableau contenant les arguments à la suite
        :param magic_method: ?Le format de fonction ?Le format de retour attendu ?
        :param magic_0: ?Unknown?
        :return: bytes
        """

        taille_paquet = len(unPaquetArguments) + TAILLE_EN_TETES
        taille_paquet_2 = taille_paquet - 34
        taille_paquet_3 = taille_paquet_2 + 2

        taille_paquet = taille_paquet.to_bytes(4, byteorder='big')
        taille_paquet_2 = taille_paquet_2.to_bytes(4, byteorder='big')
        taille_paquet_3 = taille_paquet_3.to_bytes(1, byteorder='big')

        identifiant_commande = unIdentifiantCommande.to_bytes(4, byteorder='big')
        identifiant_conversation = self.packet_id.to_bytes(2, byteorder='big')

        identifiant_balance = self._balance_id

        magic_0 = magic_0.to_bytes(2, byteorder='big')
        magic_method = magic_method.to_bytes(2, byteorder='big')

        paquet_instructions = self._construire_args(taille_paquet, CONSTANTE_UNKNOWN_1, self.balance_id,
                                                    taille_paquet_2, CLIENT_UNKNOWN_CONSTANT, bytes([0x0] * 13), magic_0,
                                                    bytes([0x00]), taille_paquet_3, CLIENT_UNKNOWN_CONSTANT, balance_target, magic_method,
                                                    identifiant_commande, CONSTANTE_UNKNOWN_0,
                                                    self.packet_id.to_bytes(2, byteorder='big'), unPaquetArguments)

        return paquet_instructions

    def creerPLU(self, unNumeroRayon, unIdentifiantPLU, uneDesignation, uneDescription, uneDate, unTarifUnitaire,
                 unCodeBarreEAN, unTypeCodeBarre=1, unTypeEtiquette=10):
        """
        Création d'un nouveau PLU dans la balance
        :param unNumeroRayon: Le numéro de rayon cible
        :param unIdentifiantPLU: Un numéro de PLU à affecter au produit
        :param uneDesignation: Une désignation PLU
        :param uneDescription: Une description du PLU
        :param uneDate: Une date (chaîne de caractères)
        :param unTarifUnitaire: Un tarif unitaire au Kg
        :param unCodeBarreEAN: Le code barre du produit cible
        :param unTypeCodeBarre: Le format de code barre
        :param unTypeEtiquette: Le format d'étiquette pour le PLU
        :return: bool
        """
        unTarifUnitaire = int(round(unTarifUnitaire * 100, 0))

        tarif_unitaire = unTarifUnitaire.to_bytes(4, byteorder='big')
        code_rayon = unNumeroRayon.to_bytes(4, byteorder='little')
        identifiant_plu = unIdentifiantPLU.to_bytes(4, byteorder='big')
        code_barre = unCodeBarreEAN.to_bytes(8, byteorder='big')
        format_code_barre = unTypeCodeBarre.to_bytes(1, byteorder='big')
        format_etiquette = unTypeEtiquette.to_bytes(1, byteorder='big')

        designation_plu = self._convertir_texte(uneDesignation)
        description_plu = self._convertir_texte(uneDescription)

        date_plu = self._convertir_texte(uneDate)

        paquet_instructions = self._construire_args(code_rayon, identifiant_plu, code_rayon, identifiant_plu,
                                                    code_barre, code_barre, bytes([0x0] * 9), code_rayon,
                                                    identifiant_plu, bytes([0x0] * 5), tarif_unitaire,
                                                    bytes([0x0] * 10), format_etiquette, code_barre, bytes.fromhex(
                '0000000001000001000000020000fffe00000000000000000000000001'), format_code_barre, bytes([0x0] * 18),
                                                    designation_plu, description_plu, date_plu, bytes([0x00] * 3))

        if self._envoyer(self._construire_paquet(COMMANDE_CREATION, paquet_instructions)) is False:
            return False

        resp = self._recuperer_reponse()

        if resp is None:
            return False

        magic_method, id_method, packet_id, data = resp

        return True

    def _initialiser(self):
        """
        Effectue la demande d'identification de la balance distante (entre autre..)
        :return: bool
        """
        # Construction d'une fonction sans argument puis execution sur balance distante
        if self._envoyer(self._construire_paquet(COMMANDE_DEMANDE_HELLO, bytes(), magic_0=0x0, balance_target=BALANCE_UNKNOWN_CONSTANT_R)) is False:
            return False

        # Attente de la réponse
        resp = self._recuperer_reponse()

        if resp is None:
            return False

        magic_method, id_method, packet_id, data = resp
        self._name = str(data, 'ascii', 'ignore') # On récupère le nom de la balance cible

        return True

    def lecturePLU(self, unNumeroRayon, unIdentifiantPLU):
        """
        Récupère la fiche PLU d'un article sur la balance distante
        :param unNumeroRayon: Le numéro de rayon cible
        :param unIdentifiantPLU: Le numéro de PLU cible
        :return:
        """
        # Convertir les valeurs en bytes
        code_rayon = unNumeroRayon.to_bytes(4, byteorder='little')
        identifiant_plu = unIdentifiantPLU.to_bytes(4, byteorder='big')

        # Construction/Payload pour appel de fonction
        paquet_instructions = self._construire_args(code_rayon, identifiant_plu, code_rayon, identifiant_plu, bytes([0x0]*24), CLIENT_UNKNOWN_CONSTANT)

        # Construction de l'en-tête et execution sur la balance
        if self._envoyer(self._construire_paquet(COMMANDE_LECTURE_PLU, paquet_instructions)) is False:
            return False

        # Attendre la réponse de la balance
        resp = self._recuperer_reponse()

        if resp is None:
            return False

        magic_method, id_method, packet_id, data = resp

        return True

    def supprimerPLU(self, unNumeroRayon, unIdentifiantPLU):
        """
        Supprime un PLU de la balance
        :param unNumeroRayon: Le numéro de rayon cible
        :param unIdentifiantPLU: Un numéro de PLU
        :return: bool
        """
        code_rayon = unNumeroRayon.to_bytes(4, byteorder='little')
        identifiant_plu = unIdentifiantPLU.to_bytes(4, byteorder='big')

        paquet_instructions = self._construire_args(code_rayon, identifiant_plu, code_rayon, identifiant_plu, bytes([0x0]*24), CLIENT_UNKNOWN_CONSTANT)

        if self._envoyer(self._construire_paquet(COMMANDE_SUPPRESSION, paquet_instructions)) is False:
            return False

        resp = self._recuperer_reponse()

        if resp is None:
            return False

        magic_method, id_method, packet_id, data = resp

        print(resp)
        return True
