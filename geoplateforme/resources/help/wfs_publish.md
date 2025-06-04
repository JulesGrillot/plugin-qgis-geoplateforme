- Description :

Publication de base de données vectorielle en service WFS.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Identifiant de l'entrepôt    | `DATASTORE`        | Identifiant de l'entrepôt utilisé pour la création de la livraison.  |
| Identifiant de la base de données vectorielle | `STORED_DATA`      | Identifiant de la base de données vectorielle. |
| Nom de la publication | `NAME`      | Nom de la publication. |
| Nom technique de la publication | `LAYER_NAME`      | Nom technique de la publication. |
| Titre de la publication | `TITLE`      | Titre de la publication. |
| Résumé de la publication | `ABSTRACT`      | Résumé de la publication. |
| Mot clé de la publication | `KEYWORDS`      | Mot clé de la publication. |
| JSON pour les relations | `RELATIONS`      | JSON pour les relations. Example : `[{"native_name" : <nom couche en base>, "public_name": <nom affiché pour la couche>,"title": titre, "abstract": résumé, "keywords": mot clé}]`.  |
| Url attribution | `URL_ATTRIBUTION`      | Url attribution |
| Titre attribution | `URL_TITLE`      | Titre attribution |
| Tags à ajouter | `TAGS`  | List de tags à importer. Format `"clé 1,valeur 1;clé 2,valeur 2;..;clé n,valeur n"` |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la publication | `OFFERING_ID`        | Identifiant de la publication  |

Nom du traitement : `geoplateforme:wfs_publish`
