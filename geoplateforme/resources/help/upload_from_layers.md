- Description :

Création d'une livraison dans un entrepôt depuis une liste de couches vectorielles.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Identifiant de l'entrepôt    | `DATASTORE`        | Identifiant de l'entrepôt utilisé pour la création de la livraison.  |
| Nom de la livraison        | `NAME`      | Nom de la livraison. |
| Description de la livraison| `DESCRIPTION`  | Description de la livraison. |
| Couches à importer | `LAYERS`  | Couches vectorielles à importer. |
| Tags à ajouter | `TAGS`  | List de tags à importer. Format `"clé 1,valeur 1;clé 2,valeur 2;..;clé n,valeur n"` |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la livraison créé | `CREATED_UPLOAD_ID`        | Identifiant de la livraison créé  |

La livraison n'est pas effectuée si les systèmes de coordonnées sont différents entre les couches.

Le traitement attends la finalisation de la livraison dans la géoplateforme avant de s'arreter.

Nom du traitement : `geoplateforme:upload_from_files`
