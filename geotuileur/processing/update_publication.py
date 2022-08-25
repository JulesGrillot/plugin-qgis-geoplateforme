# standard
import json

# PyQGIS
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geotuileur.api.configuration import ConfigurationRequestManager
from geotuileur.toolbelt import PlgLogger

data_type = "WMTS-TMS"


class UpdatePublicationAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"
    DATASTORE = "datastore"
    STORED_DATA = "stored_data"
    NAME = "name"
    TITLE = "title"
    ABSTRACT = "abstract"
    KEYWORDS = "keywords"
    LAYER_NAME = "layer_name"
    METADATA = "metadata"
    URL_TITLE = "url_title"
    URL_ATTRIBUTION = "url_attribution"
    VISIBILITY = "visibility"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return UpdatePublicationAlgorithm()

    def name(self):
        return "update publication "

    def displayName(self):
        return self.tr("Create configuration")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):

        return self.tr(
            "Publication in geotuileur platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.DATASTORE}": wanted  datastore  (str),\n'
            f'    "{self.STORED_DATA}":wanted stored data name (str),\n'
            "}\n"
        )

    def initAlgorithm(self, config=None):
        self.log = PlgLogger().log

        self.addParameter(
            QgsProcessingParameterString(
                name=self.INPUT_JSON,
                description=self.tr("Input .json file"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        filename = self.parameterAsFile(parameters, self.INPUT_JSON, context)
        self.log(message=f"Input publication configuration: {filename}", log_level=4)
        with open(filename, "r") as file:
            data = json.load(file)

            datastore = data[self.DATASTORE]
            stored_data = data[self.STORED_DATA]

            # get configuration from input data
            try:
                configuration_id_manager = ConfigurationRequestManager()
                configuration_ids = configuration_id_manager.get_configurations_id(
                    datastore, stored_data
                )

                for configuration_id in configuration_ids:
                    data = configuration_id_manager.get_configuration_info(
                        datastore, configuration_id
                    )
                name = data["name"]
                title = data["type_infos"]["title"]
                layer_name = data["layer_name"]
                abstract = data["type_infos"]["abstract"]
                url_path = data["attribution"]["url"]
                url_name = data["attribution"]["title"]
                keywords = data["type_infos"]["keywords"]
                datastore = data["_id"]
                self.log(message=f"get informations data: {data}", log_level=4)
            except (ConfigurationRequestManager.ConfigurationCreationException) as exc:
                raise QgsProcessingException(f"exc get informations data : {exc}")

            return {
                self.DATASTORE: datastore,
                self.STORED_DATA: stored_data,
                self.NAME: name,
                self.LAYER_NAME: layer_name,
                self.TITLE: title,
                self.ABSTRACT: abstract,
                self.URL_ATTRIBUTION: url_path,
                self.URL_TITLE: url_name,
                self.KEYWORDS: keywords,
            }
