# standard
import json
import os
import tempfile
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage

# Plugin
from geoplateforme.api.datastore import DatastoreRequestManager
from geoplateforme.api.metadata import MetadataRequestManager, MetadataType
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


class PublicationStatut(QWizardPage):
    def __init__(
        self,
        qwp_table_style_selection: TableRelationPageWizard,
        qwp_publication_form: PublicationFormPageWizard,
        qwp_metadata_form: MetadataFormPageWizard,
        qwp_visibility: VisibilityPageWizard,
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
        self.qwp_metadata_form = qwp_metadata_form
        self.qwp_visibility = qwp_visibility
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
            self.lbl_result.setText(self.tr("Service WMS-Vecteur publié avec succès"))
            self.offering_id = result[WmsPublicationAlgorithm.OFFERING_ID]
            try:
                metadata = self.qwp_metadata_form.metadata
                if self.qwp_metadata_form.new_metadata:
                    self.lbl_result.setText(
                        "\n".join(
                            [
                                self.lbl_result.text(),
                                self.tr("Création de la métadonnée"),
                            ]
                        )
                    )
                    manager = MetadataRequestManager()
                    manager.update_metadata_links(metadata)
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        temp_dir = Path(tmpdirname)
                        file_name = temp_dir / f"{metadata._id}.xml"
                        file_name.write_text(metadata.generate_xml_from_fields())
                        metadata_type = MetadataType("ISOAP")
                        metadata_open = True
                        metadata = manager.create_metadata(
                            datastore_id=datastore_id,
                            file_path=file_name,
                            open_data=metadata_open,
                            metadata_type=metadata_type,
                        )
                        manager.add_tags(
                            datastore_id, metadata._id, {"datasheet_name": dataset_name}
                        )

                    self.lbl_result.setText(
                        "\n".join(
                            [
                                self.lbl_result.text(),
                                self.tr("Métadonnée créée avec succès"),
                            ]
                        )
                    )
                else:
                    self.lbl_result.setText(
                        "\n".join(
                            [
                                self.lbl_result.text(),
                                self.tr("Mise à jour de la métadonnée"),
                            ]
                        )
                    )
                    manager = MetadataRequestManager()
                    manager.update_metadata(datastore_id, metadata)
                    self.lbl_result.setText(
                        "\n".join(
                            [
                                self.lbl_result.text(),
                                self.tr("Métadonnée mise à jour avec succès"),
                            ]
                        )
                    )

                # Publish metadata
                self.lbl_result.setText(
                    "\n".join(
                        [
                            self.lbl_result.text(),
                            self.tr("Publication de la métadonnée"),
                        ]
                    )
                )

                # get the endpoint for the publication
                datastore_manager = DatastoreRequestManager()
                datastore = datastore_manager.get_datastore(datastore_id)
                metadata_endpoint_id = datastore.get_endpoint(data_type="METADATA")

                # publish metadata
                manager.publish(
                    datastore_id=datastore_id,
                    endpoint_id=metadata_endpoint_id,
                    metadata_file_identifier=metadata.file_identifier,
                )

                self.lbl_result.setText(
                    "\n".join(
                        [
                            self.lbl_result.text(),
                            self.tr("Métadonnée publiée avec succès"),
                        ]
                    )
                )
            except Exception as e:
                self.lbl_result.setText(
                    self.tr("Erreur lors de l'enregistrement de la métadonnée")
                )
                self.tbw_errors.setVisible(True)
                self.tbw_errors.setText(e)
        else:
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WMS-Vecteur")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(feedback.textLog())
