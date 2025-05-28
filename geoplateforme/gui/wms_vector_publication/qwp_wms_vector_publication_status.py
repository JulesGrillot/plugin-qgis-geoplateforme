# standard
import json
import os

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QWizardPage

# Plugin
from geoplateforme.gui.wms_vector_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.gui.wms_vector_publication.qwp_table_style_selection import (
    TableRelationPageWizard,
)
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string
from geoplateforme.processing.wms_publication import WmsPublicationAlgorithm
from geoplateforme.toolbelt import PlgLogger, PlgOptionsManager


class PublicationStatut(QWizardPage):
    def __init__(
        self,
        qwp_table_style_selection: TableRelationPageWizard,
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
        self.qwp_table_style_selection = qwp_table_style_selection
        self.qwp_publication_form = qwp_publication_form
        uic.loadUi(
            os.path.join(
                os.path.dirname(__file__), "qwp_wms_vector_publication_status.ui"
            ),
            self,
        )

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
        Run WfsPublicationAlgorithm

        """
        configuration = self.qwp_publication_form.wdg_publication_form.get_config()
        datastore_id = (
            self.qwp_table_style_selection.cbx_datastore.current_datastore_id()
        )
        stored_data = (
            self.qwp_table_style_selection.cbx_stored_data.current_stored_data_id()
        )
        dataset_name = self.qwp_table_style_selection.cbx_dataset.current_dataset_name()

        params = {
            WmsPublicationAlgorithm.ABSTRACT: configuration.abstract,
            WmsPublicationAlgorithm.DATASTORE: datastore_id,
            WmsPublicationAlgorithm.KEYWORDS: "QGIS Plugin",  # TODO : define keywords
            WmsPublicationAlgorithm.LAYER_NAME: configuration.layer_name,
            WmsPublicationAlgorithm.METADATA: [],
            WmsPublicationAlgorithm.NAME: configuration.name,
            WmsPublicationAlgorithm.STORED_DATA: stored_data,
            WmsPublicationAlgorithm.TITLE: configuration.title,
            WmsPublicationAlgorithm.URL_TITLE: configuration.url_title,
            WmsPublicationAlgorithm.URL_ATTRIBUTION: configuration.url,
            WmsPublicationAlgorithm.TAGS: tags_to_qgs_parameter_matrix_string(
                {"datasheet_name": dataset_name}
            ),
        }

        selected_table_styles = (
            self.qwp_table_style_selection.get_selected_table_styles()
        )

        relations = []

        # Define relation for each selected table.
        for table_style in selected_table_styles:
            relation = {
                WmsPublicationAlgorithm.RELATIONS_NAME: table_style.native_name,
                WmsPublicationAlgorithm.RELATIONS_STYLE_FILE: table_style.stl_file,
            }
            relations.append(relation)
        params[WmsPublicationAlgorithm.RELATIONS] = json.dumps(relations)

        algo_str = f"{GeoplateformeProvider().id()}:{WmsPublicationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
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
