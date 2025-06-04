# standard
import os

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage

from geoplateforme.gui.wmts_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)

# Plugin
from geoplateforme.gui.wmts_publication.qwp_wmts_edition import WMTSEditionPageWizard
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string
from geoplateforme.processing.wmts_publication import WmtsPublicationAlgorithm


class PublicationStatut(QWizardPage):
    def __init__(
        self,
        qwp_wmts_edition: WMTSEditionPageWizard,
        qwp_publication_form: PublicationFormPageWizard,
        parent=None,
    ):
        """
        QWizardPage to define URL publication for data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Publication WMTS-TMS"))
        self.qwp_wmts_edition = qwp_wmts_edition
        self.qwp_publication_form = qwp_publication_form
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_wmts_publication_status.ui"),
            self,
        )
        self.offering_id = ""
        self.tbw_errors.setVisible(False)

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.create_publication()

    def create_publication(self) -> None:
        """
        Run WfsPublicationAlgorithm

        """
        configuration = self.qwp_publication_form.wdg_publication_form.get_config()
        datastore_id = self.qwp_wmts_edition.datastore_id
        stored_data = self.qwp_wmts_edition.stored_data_id
        dataset_name = self.qwp_wmts_edition.dataset_name

        bottom_level: int = self.qwp_wmts_edition.get_bottom_level()
        top_level: int = self.qwp_wmts_edition.get_top_level()

        params = {
            WmtsPublicationAlgorithm.ABSTRACT: configuration.abstract,
            WmtsPublicationAlgorithm.DATASTORE: datastore_id,
            WmtsPublicationAlgorithm.STORED_DATA: stored_data,
            WmtsPublicationAlgorithm.KEYWORDS: "QGIS Plugin",  # TODO : define keywords
            WmtsPublicationAlgorithm.LAYER_NAME: configuration.layer_name,
            WmtsPublicationAlgorithm.METADATA: [],
            WmtsPublicationAlgorithm.NAME: configuration.name,
            WmtsPublicationAlgorithm.BOTTOM_LEVEL: bottom_level,
            WmtsPublicationAlgorithm.TOP_LEVEL: top_level,
            WmtsPublicationAlgorithm.TITLE: configuration.title,
            WmtsPublicationAlgorithm.URL_TITLE: configuration.url_title,
            WmtsPublicationAlgorithm.URL_ATTRIBUTION: configuration.url,
            WmtsPublicationAlgorithm.TAGS: tags_to_qgs_parameter_matrix_string(
                {"datasheet_name": dataset_name}
            ),
        }

        algo_str = f"{GeoplateformeProvider().id()}:{WmtsPublicationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        result, success = alg.run(parameters=params, context=context, feedback=feedback)
        if success:
            self.lbl_result.setText(self.tr("Service WMTS-TMS publié avec succès"))
            self.offering_id = result[WmtsPublicationAlgorithm.OFFERING_ID]
        else:
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WMTS-TMS")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(feedback.textLog())
