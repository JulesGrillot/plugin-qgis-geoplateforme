# standard
import os
import tempfile
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage

# Plugin
from geoplateforme.api.custom_exceptions import ReadStoredDataException
from geoplateforme.api.metadata import MetadataRequestManager, MetadataType
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.gui.publication_creation.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.gui.qwp_metadata_form import (
    MetadataFormPageWizard,
)
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.publication.upload_publication import (
    UploadPublicationAlgorithm,
)
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string


class PublicationStatut(QWizardPage):
    def __init__(
        self,
        qwp_publication_form: PublicationFormPageWizard,
        qwp_metadata_form: MetadataFormPageWizard,
        parent=None,
    ):
        """
        QWizardPage to define URL publication for data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Publication WMTS-TMS"))
        self.qwp_publication_form = qwp_publication_form
        self.qwp_metadata_form = qwp_metadata_form
        uic.loadUi(os.path.join(os.path.dirname(__file__), "qwp_status.ui"), self)
        self.offering_id = ""
        self.tbw_errors.setVisible(False)

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
            bottom = zoom_levels_int[-1]
            top = zoom_levels_int[0]
        except ValueError as exc:
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WMTS-TMS")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(f"Invalid zoom levels value: {exc}")
            return

        params = {
            UploadPublicationAlgorithm.ABSTRACT: configuration.abstract,
            UploadPublicationAlgorithm.BOTTOM_LEVEL: bottom,
            UploadPublicationAlgorithm.DATASTORE: datastore_id,
            UploadPublicationAlgorithm.KEYWORDS: "QGIS Plugin",  # TODO : define keywords
            UploadPublicationAlgorithm.LAYER_NAME: configuration.layer_name,
            UploadPublicationAlgorithm.METADATA: [],
            UploadPublicationAlgorithm.NAME: configuration.name,
            UploadPublicationAlgorithm.STORED_DATA: stored_data,
            UploadPublicationAlgorithm.TITLE: configuration.title,
            UploadPublicationAlgorithm.TOP_LEVEL: top,
            UploadPublicationAlgorithm.URL_TITLE: configuration.url_title,
            UploadPublicationAlgorithm.URL_ATTRIBUTION: configuration.url,
            UploadPublicationAlgorithm.TAGS: tags_to_qgs_parameter_matrix_string(
                {"datasheet_name": dataset_name}
            ),
        }

        algo_str = (
            f"{GeoplateformeProvider().id()}:{UploadPublicationAlgorithm().name()}"
        )
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        result, success = alg.run(parameters=params, context=context, feedback=feedback)
        if success:
            self.lbl_result.setText(self.tr("Service WMTS-TMS publié avec succès"))
            self.offering_id = result[UploadPublicationAlgorithm.OFFERING_ID]
            try:
                if self.qwp_metadata_form.new_metadata:
                    self.lbl_result.setText(
                        "\n".join(
                            [
                                self.lbl_result.text(),
                                self.tr("Création de la métadonnée"),
                            ]
                        )
                    )
                    metadata = self.qwp_metadata_form.metadata
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
                    manager.update_metadata(
                        datastore_id, self.qwp_metadata_form.metadata
                    )
                    self.lbl_result.setText(
                        "\n".join(
                            [
                                self.lbl_result.text(),
                                self.tr("Métadonnée mise à jour avec succès"),
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
