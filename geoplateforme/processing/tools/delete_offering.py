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
    ReadOfferingException,
    UnavailableConfigurationException,
    UnavailableOfferingsException,
)
from geoplateforme.api.offerings import OfferingsRequestManager, OfferingStatus
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class DeleteOfferingAlgorithm(QgsProcessingAlgorithm):
    DATASTORE = "DATASTORE"
    OFFERING = "OFFERING"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return DeleteOfferingAlgorithm()

    def name(self):
        return "delete_offering"

    def displayName(self):
        return self.tr("Suppression d'une offre")

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
                name=self.OFFERING,
                description=self.tr("Identifiant de l'offre"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        datastore_id = self.parameterAsString(parameters, self.DATASTORE, context)
        offering_id = self.parameterAsString(parameters, self.OFFERING, context)

        manager_offer = OfferingsRequestManager()
        try:
            feedback.pushInfo(self.tr("Récupération de l'offre"))
            offering = manager_offer.get_offering(datastore_id, offering_id)

        except ReadOfferingException as exc:
            raise QgsProcessingException(
                self.tr("Erreur lors de la récupération de l'offre : {}").format(exc)
            ) from exc

        try:
            feedback.pushInfo(self.tr("Suppression de l'offre"))
            manager_offer = OfferingsRequestManager()
            manager_offer.delete_offering(datastore_id, offering_id)

        except UnavailableOfferingsException as exc:
            raise QgsProcessingException(
                self.tr("Erreur lors de la suppression de l'offre : {}").format(exc)
            ) from exc

        feedback.pushInfo(self.tr("Attente dépublication de l'offre"))
        unpublishing = True
        while unpublishing:
            try:
                offering = manager_offer.get_offering(
                    datastore=datastore_id, offering=offering_id
                )
                if offering.status != OfferingStatus.UNPUBLISHING:
                    raise QgsProcessingException(
                        self.tr(
                            "L'offre {} n'est pas en cours de dépublication. La suppression de la configuration associée est annulée."
                        ).format(offering_id)
                    )
            except ReadOfferingException:
                unpublishing = False
            if unpublishing:
                sleep(1)

        # Check if configuration is associated to another offering
        try:
            feedback.pushInfo(
                self.tr("Récupération des offres associés à la même configuration")
            )
            offering_list = manager_offer.get_offering_list(
                datastore_id=datastore_id,
                configuration_id=offering.configuration._id,
            )

        except ReadOfferingException as exc:
            raise QgsProcessingException(
                self.tr(
                    "Erreur lors de la récupération des offres de la configuration : {}"
                ).format(exc)
            ) from exc

        if len(offering_list) == 0:
            feedback.pushInfo(
                self.tr("Suppression de la configuration associée à l'offre")
            )
            manager_config = ConfigurationRequestManager()
            try:
                manager_config.delete_configuration(
                    datastore=datastore_id,
                    configuration_id=offering.configuration._id,
                )

            except UnavailableConfigurationException as exc:
                raise QgsProcessingException(
                    self.tr(
                        "Erreur lors de la suppression de la configuration associée à l'offre : {}"
                    ).format(exc)
                ) from exc

        return {}
