# standard
import json
import os

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage

# Plugin
from geoplateforme.gui.wms_vector_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.gui.wms_vector_publication.qwp_table_style_selection import (
    TableRelationPageWizard,
)
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.publication.wms_publication import WmsPublicationAlgorithm
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string


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
        self.setTitle(self.tr("Publication WMS-Vecteur"))
        self.qwp_table_style_selection = qwp_table_style_selection
        self.qwp_publication_form = qwp_publication_form
        uic.loadUi(
            os.path.join(
                os.path.dirname(__file__), "qwp_wms_vector_publication_status.ui"
            ),
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
        feedback = QgsProcessingFeedback()

        result, success = alg.run(parameters=params, context=context, feedback=feedback)
        if success:
            self.lbl_result.setText(self.tr("Service WMS-Vecteur publié avec succès"))
            self.offering_id = result[WmsPublicationAlgorithm.OFFERING_ID]
        else:
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WMS-Vecteur")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(feedback.textLog())
