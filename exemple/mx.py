from averyberkel import MX

if __name__ == '__main__':

    kAB = MX('192.168.0.50', 1)

    try:
        kAB.ouvrir()
    except averyberkel.mx.UnableInatializeScaleException as e:
        print(format(e))
        exit(-1)
    except Exception as e:
        print(format(e))
        exit(-2)

    if not kAB.creerPLU(1, 1, 'TESTProduitMX', 'Origine InconnuHaha', '2016', 10.99, 212345000000):
        print('Impossible de créer le PLU #1.')

    if not kAB.creerPLU(1, 2, 'TESTProduitMX2', 'Origine Maroc', '2018', 44.11, 232141000000):
        print('Impossible de créer le PLU #2.')

    if not kAB.creerPLU(1, 3, 'ShouldNotExist', 'Origine Inconnue', '2032', 2.66, 112341000000):
        print('Impossible de créer le PLU #3.')

    if not kAB.supprimerPLU(1, 3):
        print('Impossible de supprimer le PLU #3.')

    kAB.fermer()
