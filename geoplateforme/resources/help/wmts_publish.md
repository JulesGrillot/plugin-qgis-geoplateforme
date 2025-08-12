- Description :

Publication de tuiles raster en service WMTS-TMS.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Identifiant de l'entrepôt    | `DATASTORE`        | Identifiant de l'entrepôt utilisé pour la création de la livraison.  |
| Identifiant des tuiles raster | `STORED_DATA`      | Identifiant des tuiles raster. |
| Nom de la publication | `NAME`      | Nom de la publication. |
| Nom technique de la publication | `LAYER_NAME`      | Nom technique de la publication. |
| Titre de la publication | `TITLE`      | Titre de la publication. |
| Résumé de la publication | `ABSTRACT`      | Résumé de la publication. |
| Mot clé de la publication | `KEYWORDS`      | Mot clé de la publication. |
| Niveau bas pour la pyramide | `BOTTOM_LEVEL`      | Niveau bas pour la pyramide, valeur entre 1 et 21 |
| Niveau haut pour la pyramide | `TOP_LEVEL`      | Niveau haut pour la pyramide, valeur entre 1 et 21 |
| Identifiant fichier de style ROK4 | `STYLES`      | Identifiant des styles ROK4. Valeurs séparées par des virgules (,) |
| Ressource cible du GeFeatureInfo | `FEATURE_INFO_SERVER_URL`      | Ressource cible du GeFeatureInfo, si non défini utilisation des valeurs de la données stockée. |
| Url attribution | `URL_ATTRIBUTION`      | Url attribution |
| Titre attribution | `URL_TITLE`      | Titre attribution |
| Tags à ajouter | `TAGS`  | List de tags à importer. Format `"clé 1,valeur 1;clé 2,valeur 2;..;clé n,valeur n"` |
| Ouvert à tout public | `OPEN`      | Booléen pour ouvrir la publication |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la publication | `OFFERING_ID`        | Identifiant de la publication  |

Nom du traitement : `geoplateforme:wmts_publish`
