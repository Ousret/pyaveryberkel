# pyAveryBerkel
Contrôler votre balance de la marque Avery Berkel en Python et ce gratuitement! 
Intégrer le dans votre système sans passer par le logiciel dédié.

## Matériel compatible
Les balances de la gamme **M** sont compatibles avec ce module Python. 
Il faut que la balance soit reliée et dispose d'une adresse IP.

## Les méthodes disponibles

    - Création de PLU
    - Suppression de PLU
    - Obtenir les informations d'un PLU sur la balance

D'autre méthodes verront le jour dès que possible.

## Exemples

Répertoire ./exemple

```python
from averyberkel import MX

if __name__ == '__main__':

    # Création d'une instance MX pour la balance '192.168.0.50', id = 1 sauf si balance esclave.
    kAB = MX('192.168.0.50', 1)

    try:
        # On essaie d'ouvrir la connexion avec la balance si disponible
        kAB.ouvrir()
    except averyberkel.mx.UnableInatializeScaleException as e:
        print(format(e))
        exit(-1)
    except Exception as e:
        print(format(e))
        exit(-2)

    # On essaie de créer des PLU sur la balance
    if not kAB.creerPLU(1, 1, 'TESTProduitMX', 'Origine InconnuHaha', '2016', 10.99, 212345000000):
        print('Impossible de créer le PLU #1.')  # Ne dois pas arriver en temps normal. (Si existe, la balance écrase.)

    if not kAB.creerPLU(1, 2, 'TESTProduitMX2', 'Origine Maroc', '2018', 44.11, 232141000000):
        print('Impossible de créer le PLU #2.')

    if not kAB.creerPLU(1, 3, 'ShouldNotExist', 'Origine Inconnue', '2032', 2.66, 112341000000):
        print('Impossible de créer le PLU #3.')

    # On supprime un PLU existant sur la balance (#3)
    if not kAB.supprimerPLU(1, 3):
        print('Impossible de supprimer le PLU #3.')

    # On termine la connexion.
    kAB.fermer()  # Attention /!\ Ceci est important, sinon la balance ne libérera pas la mémoire alloué au client!
```

## Contribution

Toutes les contributions sont les bienvenues!