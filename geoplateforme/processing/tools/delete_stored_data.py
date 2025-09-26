# standard

# PyQGIS

from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.custom_exceptions import (
    DeleteStoredDataException,
    UnavailableOfferingsException,
)
from geoplateforme.api.offerings import OfferingsRequestManager
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.processing.tools.delete_offering import DeleteOfferingAlgorithm
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class DeleteStoredDataAlgorithm(QgsProcessingAlgorithm):
    DATASTORE = "DATASTORE"
    STORED_DATA = "STORED_DATA"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return DeleteStoredDataAlgorithm()

    def name(self):
        return "delete_stored_data"

    def displayName(self):
        return self.tr("Suppression d'une donnée stockée")

    def group(self):
        return self.tr("Outils géoplateforme")

    def groupId(self):
        return "tools"

    def helpUrl(self):
        return get_user_manual_url(self.name())

    def shortHelpString(self):
        return get_short_string(self.name(), self.displayName())

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                name=self.DATASTORE,
                description=self.tr("Identifiant de l'entrepôt"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.STORED_DATA,
                description=self.tr("Identifiant de la donnée stockée"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        datastore_id = self.parameterAsString(parameters, self.DATASTORE, context)
        stored_data_id = self.parameterAsString(parameters, self.STORED_DATA, context)

        try:
            feedback.pushInfo(self.tr("Récupération des offerings"))
            offering_id_manager = OfferingsRequestManager()

            offering_ids = offering_id_manager.get_offerings_id(
                datastore_id, stored_data_id
            )

        except UnavailableOfferingsException as exc:
            raise QgsProcessingException(
                self.tr("Erreur lors de la récupération des offerings : {}").format(exc)
            ) from exc

        feedback.pushInfo(self.tr("Delete offerings"))
        algo_str = f"geoplateforme:{DeleteOfferingAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        params = {
            DeleteOfferingAlgorithm.DATASTORE: datastore_id,
            DeleteOfferingAlgorithm.OFFERING: ",".join(offering_ids),
        }
        _, successful = alg.run(params, context, feedback)
        if not successful:
            raise QgsProcessingException(self.tr("Offering delete failed"))

        try:
            feedback.pushInfo(self.tr("Suppression de la donnée stockée"))
            manager_stored = StoredDataRequestManager()
            manager_stored.delete(datastore_id, stored_data_id)

        except DeleteStoredDataException as exc:
            raise QgsProcessingException(
                self.tr(
                    "Erreur lors de la suppression de la donnée stockée : {}"
                ).format(exc)
            ) from exc

        return {}
