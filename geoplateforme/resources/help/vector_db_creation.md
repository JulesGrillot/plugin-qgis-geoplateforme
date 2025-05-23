- Description :

Création d'une base de données vectorielles depuis une liste de couches vectorielles

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Identifiant de l'entrepôt    | `DATASTORE`        | Identifiant de l'entrepôt utilisé pour la création de la livraison.  |
| Nom de la livraison        | `NAME`      | Nom de la livraison. |
| Couches à importer | `LAYERS`  | Couches vectorielles à importer. |
| Fichiers additionnels à importer| `FILES`  | Fichiers additionnels à importer (séparés par ; pour fichiers multiples). |
| Système de coordonnées| `SRS`  | Système de coordonnées attendus des couches et fichier à importer. |
| Tags à ajouter | `TAGS`  | List de tags à importer. Format `"clé 1,valeur 1;clé 2,valeur 2;..;clé n,valeur n"` |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la livraison créé | `CREATED_UPLOAD_ID`        | Identifiant de la livraison créé  |
| Identifiant de la base de données créés | `CREATED_STORED_DATA_ID`        | Identifiant de la base de données créés  |
| Identifiant de l'exécution du traitement | `PROCESSING_EXEC_ID`        | Identifiant de l'exécution du traitement  |

Le traitement attends la finalisation de la création de la base de données dans la géoplateforme avant de s'arreter.

Nom du traitement : `geoplateforme:vector_db_creation`
