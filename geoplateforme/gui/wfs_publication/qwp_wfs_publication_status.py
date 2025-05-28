# standard
import json
import os

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage

# Plugin
from geoplateforme.gui.wfs_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.gui.wfs_publication.qwp_table_relation import TableRelationPageWizard
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string
from geoplateforme.processing.wfs_publication import WfsPublicationAlgorithm


class PublicationStatut(QWizardPage):
    def __init__(
        self,
        qwp_table_relation: TableRelationPageWizard,
        qwp_publication_form: PublicationFormPageWizard,
        parent=None,
    ):
        """
        QWizardPage to define URL publication for data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Publication WFS"))
        self.qwp_table_relation = qwp_table_relation
        self.qwp_publication_form = qwp_publication_form
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_wfs_publication_status.ui"),
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
        datastore_id = self.qwp_table_relation.cbx_datastore.current_datastore_id()
        stored_data = self.qwp_table_relation.cbx_stored_data.current_stored_data_id()
        dataset_name = self.qwp_table_relation.cbx_dataset.current_dataset_name()

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
            self.lbl_result.setText(self.tr("Service WMS-Vecteur publié avec succès"))
            self.offering_id = result[WfsPublicationAlgorithm.OFFERING_ID]
        else:
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WMS-Vecteur")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(feedback.textLog())
