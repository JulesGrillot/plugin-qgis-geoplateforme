- Description :

Création d'une base de données vectorielles depuis un identifiant de livraison.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Identifiant de l'entrepôt    | `DATASTORE`        | Identifiant de l'entrepôt utilisé pour la création de la livraison.  |
| Identifiant de la livraison        | `UPLOAD`      | Identifiant de la livraison. |
| Nom base de données | `STORED_DATA_NAME`  | Nom de la base de données en sortie. |
| Tags à ajouter | `TAGS`  | List de tags à importer. Format `"clé 1,valeur 1;clé 2,valeur 2;..;clé n,valeur n"` |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la base de données créés | `CREATED_STORED_DATA_ID`        | Identifiant de la base de données créés  |
| Identifiant de l'exécution du traitement | `PROCESSING_EXEC_ID`        | Identifiant de l'exécution du traitement  |

Le traitement attends la finalisation de la création de la base de données dans la géoplateforme avant de s'arreter.

Nom du traitement : `geoplateforme:upload_database_integration`
