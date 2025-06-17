- Description :

Création d'une clé basique pour l'utilisateur.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Nom de la clé    | `NAME`        | Nom de la clé  |
| Nom utilisateur  | `LOGIN`        | Nom utilisateur |
| Mot de passe  | `PASSWORD`        | Mot de passe|
| Adresses IP authorisées. Valeurs séparées par ,  | `WHITELIST`        | Adresses IP authorisées. Valeurs séparées par , |
| Adresses IP non authorisée. Valeurs séparées par , | `BLACKLIST`        | Adresses IP non authorisées. Valeurs séparées par ,|
| User-agent | `USER_AGENT`        | User-agent |
| Referer  | `REFERER`        | Referer. |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Identifiant de la clé créée | `CREATED_USER_KEY_ID`        | Identifiant de la clé créée  |

Nom du traitement : `geoplateforme:create_basic_key`
