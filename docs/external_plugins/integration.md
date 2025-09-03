# Intégration d'extension tierces

L'extension Géoplateforme a été pensé comme un point d'entrée pour la mise en avant d'extension QGIS tierces qui utilisent les données ou les API de la Géoplateforme.

Lors de l'installation de l'extension vous aurez la possibilité d'installer des extensions recommandées:

- [French Locator Filter](https://plugins.qgis.org/plugins/french_locator_filter/)

Extension utilisant l'API de géocodage et de géocodage inversé.

- [GPF - Isochrone Isodistance Itinéraire](https://plugins.qgis.org/plugins/gpf_isochrone_isodistance_itineraire/)

Extension utilisant l'API de navigation pour des calculs d'itinéraire, d'isochrone et d'isodistance.

Si vous acceptez leur installation, des menus complémentaires seront disponibles pour l'extension Géoplateforme.

Vous y trouverez les actions disponibles pour ces extensions.

## Demande d'ajout de votre extension

Les demandes d'ajout d'une extension comme recommendation par l'extension Géoplateforme doivent être traité via l'ouverture d'un ticket dans GitHub.

Vous devez décrire votre extension et son utilisation de la Géoplateforme.

Une fois votre demande validée, voici les étapes nécessaires pour finaliser l'intégration dans l'extension Géoplateforme.

### Création Pull Request pour ajout dans l'extension

Une Pull Request doit être créée pour modifier les fichiers suivants :

- `geoplateforme/metadata.txt`

Ajout du nom de votre plugin en tant que dépendances:

```
plugin_dependencies=French Locator Filter,GPF - Isochrone Isodistance Itinéraire, Mon extension géoplateforme
```

Cela correspond au nom affiché dans la recherche des extensions QGIS, défini dans la balise `name` de votre `metadata.txt`.

- `geoplateforme/constants.py`

Ajout du nom technique de votre plugin dans la constante `GPF_PLUGIN_LIST`

```
GPF_PLUGIN_LIST: list[str] = [
    "french_locator_filter",
    "gpf_isochrone_isodistance_itineraire",
    "my_geoplateforme_extension"
]
```

Attention, cela ne correspond pas au nom affiché dans les extension QGIS mais au nom du répertoire contenu dans l'archive de votre extension.

Ceci est nécessaire si vous souhaitez que des actions de votre extension soient ajoutées dans l'extension Géoplateforme.

### Méthodes à implémenter dans les extensions tierces

Si vous souhaitez ajouter des actions de votre extension dans l'extension Géoplateforme, il est nécessaire d'ajouter la fonction `create_gpf_plugins_actions` dans la classe de votre extension.

Voici un exemple :

```python
def create_gpf_plugins_actions(self, parent: QWidget) -> list[QAction]:
    """Create action to be inserted a Geoplateforme plugin

    :param parent: parent widget
    :type parent: QWidget
    :return: list of action to add in Geoplateforme plugin
    :rtype: list[QAction]
    """
    available_actions = []
    action_my_widget = QAction(
            self.tr("Mon composant graphique Géoplateforme"),
            self.iface.mainWindow(),
        )
    action_my_widget.triggered.connect(
        self._display_my_widget
    )
    return available_actions
```

Vous pouvez trouver des example plus complet dans les dépôts du [French Locator Filter](https://gitlab.com/Oslandia/qgis/french_locator_filter/-/blob/master/french_locator_filter/plugin_main.py) et de [GPF - Isochrone Isodistance Itinéraire](https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/blob/main/gpf_isochrone_isodistance_itineraire/plugin_main.py)
