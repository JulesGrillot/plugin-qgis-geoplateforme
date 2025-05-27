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
| Attendre la fermeture de la livraison ? | `WAIT_FOR_CLOSE` | Option pour attendre la fermeture de la livraison avant de sortir du traitement, permet d'attendre que toutes les vérifications soient passées. (Désactivée par défaut) |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la livraison créé | `CREATED_UPLOAD_ID`        | Identifiant de la livraison créé  |

Nom du traitement : `geoplateforme:upload_from_files`
