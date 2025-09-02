# standard
from typing import Optional

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt.QtWidgets import QWizard

# Plugin
from geoplateforme.api.custom_exceptions import ReadStoredDataException
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.gui.publication.qwp_abstract_publish_service import (
    AbstractPublishServicePage,
)
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


class PublicationStatut(AbstractPublishServicePage):
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
        """QWizardPage for WMS-TMS

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
        self.setTitle(self.tr("Publication WMTS-TMS"))

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
        Run WmtsPublicationAlgorithm

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
            self.wizard().setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)
            self.lbl_result.setText(self.tr("Service WMTS-TMS publié avec succès"))
            self.offering_id = result[WmtsPublicationAlgorithm.OFFERING_ID]
            self._update_metadata()
        else:
            self.wizard().setOption(QWizard.WizardOption.NoBackButtonOnLastPage, False)
            self.publish_error = True
            self.lbl_result.setText(
                self.tr("Erreur lors de la publication du service WMTS-TMS")
            )
            self.tbw_errors.setVisible(True)
            self.tbw_errors.setText(feedback.textLog())
