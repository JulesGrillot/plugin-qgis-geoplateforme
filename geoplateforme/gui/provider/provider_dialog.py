import logging

from qgis.gui import QgsAbstractDataSourceWidget
from qgis.PyQt.QtWidgets import QAbstractItemView, QDialogButtonBox

from geoplateforme.gui.provider.mdl_search_result import SearchResultModel
from geoplateforme.gui.provider.provider_form import Ui_ProviderForm
from geoplateforme.toolbelt import PlgLogger

logger = logging.getLogger(__name__)


class ProviderDialog(QgsAbstractDataSourceWidget, Ui_ProviderForm):
    """
    Boite de dialogue de sélection des couches
    """

    def __init__(self, iface):
        super(ProviderDialog, self).__init__()

        self.iface = iface
        self.setupUi(self)

        self.log = PlgLogger().log

        self.mdl_search_result = SearchResultModel()
        self.tbv_results.setModel(self.mdl_search_result)
        self.tbv_results.verticalHeader().setVisible(False)
        self.tbv_results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # self.tbv_results.pressed.connect(
        #     lambda index: self._item_clicked(index, self.mdl_search_result, self.tbv_results)
        # )

        self.buttonBox.button(QDialogButtonBox.Apply).setText("Ajouter")
        self.buttonBox.button(QDialogButtonBox.Apply).setEnabled(False)

        self.le_search.textChanged.connect(self._onTextChanged)
        self.buttonBox.clicked.connect(self.onAccept)

    def _onTextChanged(self, text):
        if len(text) > 2:
            self.mdl_search_result.set_search_text(text)

    def onAccept(self, button):
        """
        Lorsque l'utilisateur valide
        """
        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ApplyRole:
            self.accept()
