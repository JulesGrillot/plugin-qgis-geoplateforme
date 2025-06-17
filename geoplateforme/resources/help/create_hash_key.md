- Description :

Création d'une clé hash pour l'utilisateur.

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
| Valeur du hash | `CREATED_HASH`        | Valeur du hash  |

Nom du traitement : `geoplateforme:create_hash_key`
