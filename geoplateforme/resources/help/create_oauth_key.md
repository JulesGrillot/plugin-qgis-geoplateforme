- Description :

Création d'une clé OAuth2 pour l'utilisateur. Une erreur sera retournée si une clé OAuth2 est déjà existante.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Nom de la clé    | `NAME`        | Nom de la clé  |
| Adresses IP authorisées. Valeurs séparées par ,  | `WHITELIST`        | Adresses IP authorisées. Valeurs séparées par , |
| Adresses IP non authorisée. Valeurs séparées par , | `BLACKLIST`        | Adresses IP non authorisées. Valeurs séparées par ,|
| User-agent | `USER_AGENT`        | User-agent |
| Referer  | `REFERER`        | Referer. |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la clé créée | `CREATED_USER_KEY_ID`        | Identifiant de la clé créée  |

Nom du traitement : `geoplateforme:create_oauth_key`
