# standard

# PyQGIS
from time import sleep

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
    ReadOfferingException,
    UnavailableConfigurationException,
    UnavailableOfferingsException,
)
from geoplateforme.api.offerings import OfferingsRequestManager, OfferingStatus
from geoplateforme.api.stored_data import StoredDataRequestManager
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
        try:
            feedback.pushInfo(self.tr("Récupération des configurations"))
            configuration_id_manager = ConfigurationRequestManager()
            configuration_ids = configuration_id_manager.get_configurations_id(
                datastore_id, stored_data_id
            )
        except UnavailableConfigurationException as exc:
            raise QgsProcessingException(
                self.tr(
                    "Erreur lors de la récupération des configurations : {}"
                ).format(exc)
            ) from exc

        if len(offering_ids) != 0:
            try:
                feedback.pushInfo(self.tr("Suppression des offerings"))
                for offering_id in offering_ids:
                    offering_id_manager.delete_offering(datastore_id, offering_id)

            except UnavailableOfferingsException as exc:
                raise QgsProcessingException(
                    self.tr("Erreur lors de la suppression des offerings : {}").format(
                        exc
                    )
                ) from exc

            feedback.pushInfo(self.tr("Attente déplublication des offerings"))

            nb_unpublished_offering = 0
            while nb_unpublished_offering != len(offering_ids):
                nb_unpublished_offering = 0
                for offering_id in offering_ids:
                    try:
                        offering = offering_id_manager.get_offering(
                            datastore=datastore_id, offering=offering_id
                        )
                    except ReadOfferingException:
                        nb_unpublished_offering += 1
                        continue

                    if offering.status == OfferingStatus.UNSTABLE:
                        raise QgsProcessingException(
                            self.tr("L'offering {} est en état instable.").format(
                                offering_id
                            )
                        )
                if nb_unpublished_offering != len(offering_ids):
                    sleep(1)

        if len(configuration_ids) != 0:
            try:
                feedback.pushInfo(self.tr("Suppression des configurations"))
                for configuration_id in configuration_ids:
                    configuration_id_manager.delete_configuration(
                        datastore_id, configuration_id
                    )

            except UnavailableConfigurationException as exc:
                raise QgsProcessingException(
                    self.tr(
                        "Erreur lors de la suppression des configurations : {}"
                    ).format(exc)
                ) from exc
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
