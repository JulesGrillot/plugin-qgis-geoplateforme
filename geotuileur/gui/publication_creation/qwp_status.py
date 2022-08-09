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
from geotuileur.__about__ import __title_clean__
from geotuileur.api.stored_data import StoredDataRequestManager
from geotuileur.gui.publication_creation.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geotuileur.processing import GeotuileurProvider
from geotuileur.processing.upload_publication import UploadPublicationAlgorithm
from geotuileur.toolbelt import PlgLogger


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
        self.qwp_publication_form = qwp_publication_form
        uic.loadUi(os.path.join(os.path.dirname(__file__), "qwp_status.ui"), self)

        self.log = PlgLogger().log
        self.btn_data.clicked.connect(lambda: self.openUrl(self.url_data))
        self.btn_publication.clicked.connect(lambda: self.openUrl(self.url_publication))

    def openUrl(self, url_edit) -> None:
        QDesktopServices.openUrl(QUrl(url_edit))

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

        # Getting zoom levels parameters
        manager = StoredDataRequestManager()
        try:
            stored_data_levels = manager.get_stored_data(datastore_id, stored_data)
            zoom_levels = stored_data_levels.zoom_levels()
            bottom = zoom_levels[-1]
            top = zoom_levels[0]

        except StoredDataRequestManager.ReadStoredDataException as exc:
            self.log(
                f"Error while getting zoom levels from stored data: {exc}",
                log_level=2,
                push=False,
            )

        data = {
            UploadPublicationAlgorithm.ABSTRACT: configuration.abstract,
            UploadPublicationAlgorithm.BOTTOM_LEVEL: bottom,
            UploadPublicationAlgorithm.DATASTORE: datastore_id,
            UploadPublicationAlgorithm.KEYWORDS: "Adresse",
            UploadPublicationAlgorithm.LAYER_NAME: configuration.layer_name,
            UploadPublicationAlgorithm.METADATA: [],
            UploadPublicationAlgorithm.NAME: configuration.name,
            UploadPublicationAlgorithm.STORED_DATA: stored_data,
            UploadPublicationAlgorithm.TITLE: configuration.title,
            UploadPublicationAlgorithm.TOP_LEVEL: top,
            UploadPublicationAlgorithm.TYPE_DATA: "WMTS-TMS",
            UploadPublicationAlgorithm.URL_TITLE: configuration.url_title,
            UploadPublicationAlgorithm.URL_ATTRIBUTION: configuration.url,
        }
        filename = tempfile.NamedTemporaryFile(
            prefix=f"qgis_{__title_clean__}_", suffix=".json"
        ).name
        with open(filename, "w") as file:
            json.dump(data, file)

        algo_str = f"{GeotuileurProvider().id()}:{UploadPublicationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        params = {UploadPublicationAlgorithm.INPUT_JSON: filename}
        context = QgsProcessingContext()
        self.create_url_feedback = QgsProcessingFeedback()

        result, success = alg.run(
            parameters=params, context=context, feedback=self.create_url_feedback
        )
        if success:
            url_data = result["publication_url"]

            self.log(
                message=f"result configuration_id and url_data: { result}",
                log_level=4,
            )

            url_data = url_data[6 : len(url_data) - 2]
            self.url_data = url_data
            self.url_publication = (
                "https://qlf-portail-gpf-beta.ign.fr/viewer?tiles_url=https://qlf-vt-gpf-beta.ign.fr/"
                + str(url_data[31::])
            )
            manager = StoredDataRequestManager()
            manager.add_tags(
                datastore=self.qwp_publication_form.cbx_datastore.current_datastore_id(),
                stored_data=self.qwp_publication_form.cbx_stored_data.current_stored_data_id(),
                tags={"tms_url": url_data},
            )

        else:
            self.btn_publication.setEnabled(False)
            self.btn_data.setEnabled(False)

            self.log(
                "URL publication failed \nCheck your storage capacity and the flux name \n \n "
                + self.create_url_feedback.textLog(),
                log_level=1,
                push=True,
                button=True,
                duration=60,
            )
