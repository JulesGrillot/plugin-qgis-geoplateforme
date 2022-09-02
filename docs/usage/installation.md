# Installation

## Version stable (recommandée)

Le plugin {{ title }} est publié sur le dépôt officiel des extensions de QGIS : <https://plugins.qgis.org/plugins/geotuileur/>.

## Versions expérimentales

Des versions intermédiaires (alpha, beta...) sont parfois publiées sur le dépôt officiel dans le canal expérimental.  
Pour y accéder, il suffit d'activer les extensions expérimentales dans les préférences du gestionnaire d'extensions de QGIS.

## Version en développement

Si vous vous considérez comme un *early adopter*, un testeur ou que vous ne pouvez attendre qu'une version soit publiée (même dans le canal expérimental !), vous pouvez utiliser la version automatiquement packagée pour chaque commit poussé sur la branche principale.

:::{important}
Attention, cette version est potentiellement instable.  
Il est recommandé de [se créer un profil QGIS dédié](https://docs.qgis.org/latest/fr/docs/user_manual/introduction/qgis_configuration.html#working-with-user-profiles) pour installer et tester le plugin.
:::

Pour cela :

1. Ajouter cette URL dans les dépôts référencés dans le gestionnaire d'extensions de QGIS :

    ```html
    https://oslandia.gitlab.io/qgis/ign-vectuileur/plugins.xml
    ```

    ![Dépôt personnalisé d'extensions QGIS](/static/images/qgis_extensions_custom_repository.png)

1. Activer les extensions expérimentales et la recherche de mise à jour au démarrage

    ![Paramètres du gestionnaire d'extensions QGIS](/static/images/qgis_extensions_settings.png)

1. Installer l'extension depuis l'onglet `Non installées`
1. L'activer si besoin dans `Installées` et désactiver les extensions inutiles (pour améliorer les performances et réduire la surface de diagnostic)

    ![Extensions installées](/static/images/qgis_extensions_installed.png)
