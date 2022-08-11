import json

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFile,
)
from qgis.PyQt.QtCore import QCoreApplication

from geotuileur.api.configuration import ConfigurationRequestManager

# Plugin
from geotuileur.api.offerings import OfferingsRequestManager


class UnpublishAlgorithm(QgsProcessingAlgorithm):

    INPUT_JSON = "INPUT_JSON"
    DATASTORE = "datastore"
    STORED_DATA = "stored data"

    def tr(self, string):
        return QCoreApplication.translate(
            "Unpublish for IGN Geotuileur platform", string
        )

    def createInstance(self):
        return UnpublishAlgorithm()

    def name(self):
        return "Unpublish"

    def displayName(self):
        return self.tr("Unpublish")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):
        return self.tr(
            "Unpublish in geotuileur platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.DATASTORE}": datastore id (str),\n'
            f'    "{self.STORED_DATA}": stored data(str),\n'
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT_JSON,
                description=self.tr("Input .json file"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        filename = self.parameterAsFile(parameters, self.INPUT_JSON, context)

        # load processing unpublish from the JSON

        with open(filename, "r") as file:
            data = json.load(file)
            datastore = data.get(self.DATASTORE)
            stored_data = data.get(self.STORED_DATA)

            # Getting and delete offering and configuration

        try:
            configuration_id_manager = ConfigurationRequestManager()
            offering_id_manager = OfferingsRequestManager()

            offering_ids = offering_id_manager.get_offerings_id(datastore, stored_data)
            configuration_ids = configuration_id_manager.get_configurations_id(
                datastore, stored_data
            )
            for offering_id in offering_ids:
                offering_id_manager.delete_offering(datastore, offering_id)

            for configuration_id in configuration_ids:
                configuration_id_manager.delete_configuration(
                    datastore, configuration_id
                )

        except (
            OfferingsRequestManager.UnavailableOfferingsException,
            ConfigurationRequestManager.UnavailableConfigurationException,
        ) as exc:
            raise QgsProcessingException(f"exc unpublish : {exc}")

        return {}
