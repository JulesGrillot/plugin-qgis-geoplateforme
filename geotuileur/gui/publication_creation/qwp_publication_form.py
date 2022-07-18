# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage


class PublicationFormPageWizard(QWizardPage):
    def __init__(self, parent=None):

        """
        QWizardPage to define current geotuileur publication

        Args:None

        """

        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_publication_form.ui"), self
        )

        # Only display pyramid generation ready for publication
        self.cbx_stored_data.set_filter_type(["ROK4-PYRAMID-VECTOR"])
        self.cbx_stored_data.set_expected_tags(
            ["upload_id", "proc_int_id", "pyramid_id"]
        )

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)

        self._datastore_updated()

        self.setCommitPage(True)

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        if (
            len(self.wdg_publication_form.lne_name.text()) == 0
            or len(self.wdg_publication_form.lne_title.text()) == 0
            or len(self.wdg_publication_form.txe_abstract.toPlainText()) == 0
            or len(self.wdg_publication_form.lne_legal_notice.text()) == 0
            or len(self.wdg_publication_form.lne_url_legal.text()) == 0
        ):
            valid = False
            QMessageBox.warning(
                self,
                self.tr("Missing informations."),
                self.tr("Please fill all fields."),
            )
        else:
            valid = True

        return valid

    def _datastore_updated(self) -> None:
        """
        Update pyramid generation combobox when datastore is updated

        """

        self.cbx_stored_data.set_datastore(self.cbx_datastore.current_datastore_id())
