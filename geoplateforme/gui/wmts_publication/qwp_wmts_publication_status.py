# standard
import os
import tempfile
from pathlib import Path
from typing import Optional

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage

# Plugin
from geoplateforme.api.custom_exceptions import ReadStoredDataException
from geoplateforme.api.datastore import DatastoreRequestManager
from geoplateforme.api.metadata import MetadataRequestManager, MetadataType
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.gui.publication.qwp_visibility import VisibilityPageWizard
from geoplateforme.gui.qwp_metadata_form import MetadataFormPageWizard
from geoplateforme.gui.wmts_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.publication.wmts_publication import (
    WmtsPublicationAlgorithm,
)
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string


class PublicationStatut(QWizardPage):
    def __init__(
        self,
        qwp_publication_form: PublicationFormPageWizard,
        qwp_metadata_form: MetadataFormPageWizard,
        qwp_visibility: VisibilityPageWizard,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
        parent=None,
    ):
        """
        QWizardPage to define URL publication for data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Publication WMTS-TMS"))
        self.datastore_id = datastore_id
        self.dataset_name = dataset_name
        self.stored_data_id = stored_data_id

        self.qwp_publication_form = qwp_publication_form
        self.qwp_metadata_form = qwp_metadata_form
        self.qwp_visibility = qwp_visibility
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
        datastore_id = self.datastore_id
        stored_data = self.stored_data_id
        dataset_name = self.dataset_name

        # Getting zoom levels parameters
        manager = StoredDataRequestManager()
        try:
            stored_data_levels = manager.get_stored_data(datastore_id, stored_data)
            zoom_levels = stored_data_levels.zoom_levels()
        except ReadStoredDataException as exc:
            self.lbl_result.setText(
                self.tr(
                    "Erreur lors de récupération de la données stockées pour les niveaux de zoom"
                )
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(exc)
            return

        try:
            zoom_levels_int = [int(zoom_level) for zoom_level in zoom_levels]
            zoom_levels_int = sorted(zoom_levels_int)
            bottom_level = zoom_levels_int[-1]
            top_level = zoom_levels_int[0]
        except ValueError as exc:
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WMS-Raster")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(f"Invalid zoom levels value: {exc}")
            return

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
            WmtsPublicationAlgorithm.OPEN: self.qwp_visibility.is_open(),
        }

        algo_str = f"{GeoplateformeProvider().id()}:{WmtsPublicationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        result, success = alg.run(parameters=params, context=context, feedback=feedback)
        if success:
            self.lbl_result.setText(self.tr("Service WMTS-TMS publié avec succès"))
            self.offering_id = result[WmtsPublicationAlgorithm.OFFERING_ID]
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
                self.tr("Erreur lors de la publication du service WMTS-TMS")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(feedback.textLog())
