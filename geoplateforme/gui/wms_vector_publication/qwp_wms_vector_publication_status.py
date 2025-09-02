# standard
import json
from typing import Optional

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt.QtWidgets import QWizard

# Plugin
from geoplateforme.gui.publication.qwp_abstract_publish_service import (
    AbstractPublishServicePage,
)
from geoplateforme.gui.publication.qwp_visibility import VisibilityPageWizard
from geoplateforme.gui.qwp_metadata_form import MetadataFormPageWizard
from geoplateforme.gui.wms_vector_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.gui.wms_vector_publication.qwp_table_style_selection import (
    TableRelationPageWizard,
)
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.publication.wms_publication import WmsPublicationAlgorithm
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string


class PublicationStatut(AbstractPublishServicePage):
    def __init__(
        self,
        qwp_table_style_selection: TableRelationPageWizard,
        qwp_publication_form: PublicationFormPageWizard,
        qwp_metadata_form: MetadataFormPageWizard,
        qwp_visibility: VisibilityPageWizard,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
        parent=None,
    ):
        """QWizardPage for WMS Vector publication

        :param qwp_table_style_selection: page with table relation definition
        :type qwp_table_style_selection: TableRelationPageWizard
        :param qwp_publication_form: page with configuration definition
        :type qwp_publication_form: PublicationFormPageWizard
        :param qwp_metadata_form: page with metadata definition
        :type qwp_metadata_form: MetadataFormPageWizard
        :param qwp_visibility: page with visibility definition
        :type qwp_visibility: VisibilityPageWizard
        :param datastore_id: datastore id, defaults to None
        :type datastore_id: Optional[str], optional
        :param dataset_name: dataset name, defaults to None
        :type dataset_name: Optional[str], optional
        :param stored_data_id: stored data id, defaults to None
        :type stored_data_id: Optional[str], optional
        :param parent: parent, defaults to None
        :type parent: _type_, optional
        """
        super().__init__(
            qwp_metadata_form, datastore_id, dataset_name, stored_data_id, parent
        )
        self.setTitle(self.tr("Publication WMS-Vecteur"))
        self.qwp_table_style_selection = qwp_table_style_selection
        self.qwp_publication_form = qwp_publication_form
        self.qwp_visibility = qwp_visibility

        self.datastore_id = datastore_id
        self.dataset_name = dataset_name
        self.stored_data_id = stored_data_id
        self.offering_id = ""
        self.tbw_errors.setVisible(False)

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.clear_errors()
        self.create_publication()

    def create_publication(self) -> None:
        """
        Run WmsPublicationAlgorithm

        """
        configuration = self.qwp_publication_form.wdg_publication_form.get_config()
        datastore_id = self.datastore_id
        stored_data = self.stored_data_id
        dataset_name = self.dataset_name

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
            WmsPublicationAlgorithm.OPEN: self.qwp_visibility.is_open(),
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
            self.wizard().setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)
            self.lbl_result.setText(self.tr("Service WMS-Vecteur publié avec succès"))
            self.offering_id = result[WmsPublicationAlgorithm.OFFERING_ID]
            self._update_metadata()
        else:
            self.wizard().setOption(QWizard.WizardOption.NoBackButtonOnLastPage, False)
            self.publish_error = True
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WMS-Vecteur")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(feedback.textLog())
