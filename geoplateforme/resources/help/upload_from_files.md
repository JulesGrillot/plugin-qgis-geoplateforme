- Description :

Création d'une livraison dans un entrepôt depuis une liste de fichiers.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Identifiant de l'entrepôt    | `DATASTORE`        | Identifiant de l'entrepôt utilisé pour la création de la livraison.  |
| Nom de la livraison        | `NAME`      | Nom de la livraison. |
| Description de la livraison| `DESCRIPTION`  | Description de la livraison. |
| Fichiers à importer| `FILES`  | Fichiers à importer (séparés par ; pour fichiers multiples). |
| Système de coordonnées| `SRS`  | Système de coordonnées des fichiers à importer. |
| Tags à ajouter | `TAGS`  | List de tags à importer. Format `"clé 1,valeur 1;clé 2,valeur 2;..;clé n,valeur n"` |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la livraison créé | `CREATED_UPLOAD_ID`        | Identifiant de la livraison créé  |

Le traitement attends la finalisation de la livraison dans la géoplateforme avant de s'arreter.

Nom du traitement : `geoplateforme:upload_from_files`
