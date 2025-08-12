- Description :

Publication de tuiles vectorielles.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Identifiant de l'entrepôt    | `DATASTORE`        | Identifiant de l'entrepôt utilisé pour la création de la livraison.  |
| Identifiant des tuiles vectorielles | `STORED_DATA`      | Identifiant des tuiles vectorielles. |
| Nom de la publication | `NAME`      | Nom de la publication. |
| Nom technique de la publication | `LAYER_NAME`      | Nom technique de la publication. |
| Titre de la publication | `TITLE`      | Titre de la publication. |
| Résumé de la publication | `ABSTRACT`      | Résumé de la publication. |
| Mot clé de la publication | `KEYWORDS`      | Mot clé de la publication. |
| Niveau bas pour la pyramide | `BOTTOM_LEVEL`      | Niveau bas pour la pyramide, valeur entre 1 et 21 |
| Niveau haut pour la pyramide | `TOP_LEVEL`      | Niveau haut pour la pyramide, valeur entre 1 et 21 |
| Url attribution | `URL_ATTRIBUTION`      | Url attribution |
| Titre attribution | `URL_TITLE`      | Titre attribution |
| Tags à ajouter | `TAGS`  | List de tags à importer. Format `"clé 1,valeur 1;clé 2,valeur 2;..;clé n,valeur n"` |
| Ouvert à tout public | `OPEN`      | Booléen pour ouvrir la publication |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la publication | `OFFERING_ID`        | Identifiant de la publication  |

Nom du traitement : `geoplateforme:vector_tile_publish`
