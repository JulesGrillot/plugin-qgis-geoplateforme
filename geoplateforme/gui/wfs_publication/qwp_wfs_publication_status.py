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
from geoplateforme.gui.wfs_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.gui.wfs_publication.qwp_table_relation import TableRelationPageWizard
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.publication.wfs_publication import WfsPublicationAlgorithm
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string


class PublicationStatut(AbstractPublishServicePage):
    def __init__(
        self,
        qwp_table_relation: TableRelationPageWizard,
        qwp_publication_form: PublicationFormPageWizard,
        qwp_metadata_form: MetadataFormPageWizard,
        qwp_visibility: VisibilityPageWizard,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
        parent=None,
    ):
        """QWizardPage for WFS publication

        :param qwp_table_relation: page with table relation definition
        :type qwp_table_relation: TableRelationPageWizard
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
        self.setTitle(self.tr("Publication WFS"))
        self.qwp_table_relation = qwp_table_relation
        self.qwp_publication_form = qwp_publication_form
        self.qwp_metadata_form = qwp_metadata_form
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
        Run WfsPublicationAlgorithm

        """
        configuration = self.qwp_publication_form.wdg_publication_form.get_config()
        datastore_id = self.datastore_id
        stored_data = self.stored_data_id
        dataset_name = self.dataset_name

        params = {
            WfsPublicationAlgorithm.ABSTRACT: configuration.abstract,
            WfsPublicationAlgorithm.DATASTORE: datastore_id,
            WfsPublicationAlgorithm.KEYWORDS: "QGIS Plugin",  # TODO : define keywords
            WfsPublicationAlgorithm.LAYER_NAME: configuration.layer_name,
            WfsPublicationAlgorithm.METADATA: [],
            WfsPublicationAlgorithm.NAME: configuration.name,
            WfsPublicationAlgorithm.STORED_DATA: stored_data,
            WfsPublicationAlgorithm.TITLE: configuration.title,
            WfsPublicationAlgorithm.URL_TITLE: configuration.url_title,
            WfsPublicationAlgorithm.URL_ATTRIBUTION: configuration.url,
            WfsPublicationAlgorithm.TAGS: tags_to_qgs_parameter_matrix_string(
                {"datasheet_name": dataset_name}
            ),
            WfsPublicationAlgorithm.OPEN: self.qwp_visibility.is_open(),
        }

        selected_table_relations = (
            self.qwp_table_relation.get_selected_table_relations()
        )

        relations = []

        # Define relation for each selected table.
        for table_relation in selected_table_relations:
            relation = {
                WfsPublicationAlgorithm.RELATIONS_NATIVE_NAME: table_relation.native_name,
                WfsPublicationAlgorithm.RELATIONS_TITLE: table_relation.title,
                WfsPublicationAlgorithm.RELATIONS_ABSTRACT: table_relation.native_name,
            }
            if table_relation.public_name:
                relation[WfsPublicationAlgorithm.RELATIONS_PUBLIC_NAME] = (
                    table_relation.public_name
                )
            if table_relation.keywords:
                relation[WfsPublicationAlgorithm.RELATIONS_KEYWORDS] = (
                    table_relation.keywords
                )

            relations.append(relation)
        params[WfsPublicationAlgorithm.RELATIONS] = json.dumps(relations)

        algo_str = f"{GeoplateformeProvider().id()}:{WfsPublicationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        result, success = alg.run(parameters=params, context=context, feedback=feedback)
        if success:
            self.wizard().setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)
            self.lbl_result.setText(self.tr("Service WFS publié avec succès"))
            self.offering_id = result[WfsPublicationAlgorithm.OFFERING_ID]
            self._update_metadata()
        else:
            self.wizard().setOption(QWizard.WizardOption.NoBackButtonOnLastPage, False)
            self.publish_error = True
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WFS")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(feedback.textLog())
