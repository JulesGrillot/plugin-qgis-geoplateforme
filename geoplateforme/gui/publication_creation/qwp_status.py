# standard
import json
import os
import tempfile

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QWizardPage

# Plugin
from geoplateforme.__about__ import __title_clean__
from geoplateforme.api.custom_exceptions import ReadStoredDataException
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.gui.publication_creation.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.upload_publication import UploadPublicationAlgorithm
from geoplateforme.toolbelt import PlgLogger, PlgOptionsManager


class PublicationStatut(QWizardPage):
    def __init__(
        self,
        qwp_publication_form: PublicationFormPageWizard,
        parent=None,
    ):
        """
        QWizardPage to define URL publication for data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Publication URL"))
        self.url_data = ""
        self.url_publication = ""
        self.qwp_publication_form = qwp_publication_form
        uic.loadUi(os.path.join(os.path.dirname(__file__), "qwp_status.ui"), self)

        self.log = PlgLogger().log
        self.btn_data.clicked.connect(lambda: self._openUrl(self.url_data))
        self.btn_publication.clicked.connect(
            lambda: self._openUrl(self.url_publication)
        )

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.create_publication()

    def create_publication(self) -> None:
        """
        Run UploadPublicationAlgorithm

        """
        configuration = self.qwp_publication_form.wdg_publication_form.get_config()
        datastore_id = self.qwp_publication_form.cbx_datastore.current_datastore_id()
        stored_data = self.qwp_publication_form.cbx_stored_data.current_stored_data_id()
        dataset_name = self.qwp_publication_form.cbx_dataset.current_dataset_name()

        # Getting zoom levels parameters
        manager = StoredDataRequestManager()
        try:
            stored_data_levels = manager.get_stored_data(datastore_id, stored_data)
            zoom_levels = stored_data_levels.zoom_levels()
        except ReadStoredDataException as exc:
            self.log(
                f"Error while getting zoom levels from stored data: {exc}",
                log_level=2,
                push=False,
            )
            return

        try:
            zoom_levels_int = [int(zoom_level) for zoom_level in zoom_levels]
            zoom_levels_int = sorted(zoom_levels_int)
            bottom = zoom_levels[-1]
            top = zoom_levels[0]
        except ValueError as exc:
            self.log(
                f"Invalid zoom levels value: {exc}",
                log_level=2,
                push=False,
            )
            return

        data = {
            UploadPublicationAlgorithm.ABSTRACT: configuration.abstract,
            UploadPublicationAlgorithm.BOTTOM_LEVEL: bottom,
            UploadPublicationAlgorithm.DATASTORE: datastore_id,
            UploadPublicationAlgorithm.DATASET_NAME: dataset_name,
            UploadPublicationAlgorithm.KEYWORDS: "QGIS Plugin",  # TODO : define keywords
            UploadPublicationAlgorithm.LAYER_NAME: configuration.layer_name,
            UploadPublicationAlgorithm.METADATA: [],
            UploadPublicationAlgorithm.NAME: configuration.name,
            UploadPublicationAlgorithm.STORED_DATA: stored_data,
            UploadPublicationAlgorithm.TITLE: configuration.title,
            UploadPublicationAlgorithm.TOP_LEVEL: top,
            UploadPublicationAlgorithm.URL_TITLE: configuration.url_title,
            UploadPublicationAlgorithm.URL_ATTRIBUTION: configuration.url,
        }
        filename = tempfile.NamedTemporaryFile(
            prefix=f"qgis_{__title_clean__}_", suffix=".json"
        ).name
        with open(filename, "w") as file:
            json.dump(data, file)

        algo_str = (
            f"{GeoplateformeProvider().id()}:{UploadPublicationAlgorithm().name()}"
        )
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        params = {UploadPublicationAlgorithm.INPUT_JSON: filename}
        context = QgsProcessingContext()
        create_url_feedback = QgsProcessingFeedback()

        result, success = alg.run(
            parameters=params, context=context, feedback=create_url_feedback
        )
        if success:
            self.url_data = result["publication_url"]
            plg_settings = PlgOptionsManager.get_plg_settings()
            url_geoplateforme = plg_settings.url_geoplateforme
            self.url_publication = (
                f"{url_geoplateforme}viewer?tiles_url={self.url_data}"
            )

        else:
            self.btn_publication.setEnabled(False)
            self.btn_data.setEnabled(False)

            self.log(
                "URL publication failed \nCheck your storage capacity and the flux name \n \n "
                + create_url_feedback.textLog(),
                log_level=1,
                push=True,
                button=True,
                duration=60,
            )

    @staticmethod
    def _openUrl(url_edit) -> None:
        QDesktopServices.openUrl(QUrl(url_edit))
