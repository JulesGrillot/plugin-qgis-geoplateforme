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
from geoplateforme.api.configuration import ConfigurationRequestManager
from geoplateforme.api.custom_exceptions import (
    DeleteStoredDataException,
    UnavailableOfferingsException,
    UnavailableStoredData,
)
from geoplateforme.api.offerings import OfferingsRequestManager
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.toolbelt import PlgLogger


class DeleteDataAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"
    DATASTORE = "datastore"
    STORED_DATA = "stored_data"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return DeleteDataAlgorithm()

    def name(self):
        return "delete data "

    def displayName(self):
        return self.tr("Delete data")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):
        return self.tr(
            "Delete data action in geoplateforme platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.DATASTORE}": wanted  datastore id (str),\n'
            f'    "{self.STORED_DATA}":wanted stored data id (str),\n'
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
        self.log(message=f"delete data: {filename}", log_level=4)

        # load processing  from the JSON
        with open(filename, "r") as file:
            data = json.load(file)
            datastore_id = data[self.DATASTORE]
            stored_data_id = data[self.STORED_DATA]
            try:
                manager_stored = StoredDataRequestManager()
                result = manager_stored.get_stored_data(datastore_id, stored_data_id)
            except UnavailableStoredData as exc:
                raise QgsProcessingException(f"exc publication url : {exc}")

            if "tms_url" in result.tags:
                try:
                    configuration_id_manager = ConfigurationRequestManager()
                    offering_id_manager = OfferingsRequestManager()

                    offering_ids = offering_id_manager.get_offerings_id(
                        datastore_id, stored_data_id
                    )
                    configuration_ids = configuration_id_manager.get_configurations_id(
                        datastore_id, stored_data_id
                    )
                    for offering_id in offering_ids:
                        offering_id_manager.delete_offering(datastore_id, offering_id)

                    for configuration_id in configuration_ids:
                        configuration_id_manager.delete_configuration(
                            datastore_id, configuration_id
                        )
                except UnavailableOfferingsException as exc:
                    raise QgsProcessingException(f"exc publication url : {exc}")

            try:
                manager_stored.delete(datastore_id, stored_data_id)

            except DeleteStoredDataException as exc:
                raise QgsProcessingException(f"exc publication url : {exc}")

        return {}
