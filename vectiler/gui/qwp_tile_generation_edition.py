# standard
import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWizardPage
from qgis.PyQt import uic


class TileGenerationEditionPageWizard(QWizardPage):

    STORED_DATA_ID_FIELD = "stored_data_id"

    def __init__(self, parent=None):

        """
        QWizardPage to define tile parameters

        Args:
            parent: parent QObject
        """

        super().__init__(parent)

        uic.loadUi(os.path.join(os.path.dirname(__file__), "qwp_tile_generation_edition.ui"), self)

        # Only display stored data ready for pyramid generation
        self.cbx_stored_data.set_filter_type(["VECTOR-DB"])
        self.cbx_stored_data.set_expected_tags(["upload_id", "proc_int_id"])
        self.cbx_stored_data.set_forbidden_tags(["pyramid_id"])

        self.cbx_datastore.currentIndexChanged.connect(self.datastore_updated)

        self.datastore_updated()

        # To avoid some characters
        rx = QtCore.QRegExp("[a-z-A-Z-0-9-_]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lne_flux.setValidator(validator)

        self.registerField(self.STORED_DATA_ID_FIELD, self.cbx_stored_data)

    def datastore_updated(self) -> None:
        self.cbx_stored_data.set_datastore(self.cbx_datastore.current_datastore_id())
