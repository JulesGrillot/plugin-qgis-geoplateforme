# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

# plugin
from geotuileur.api.user import User
from geotuileur.gui.gui_commons import GuiCommonUtils
from geotuileur.gui.mdl_datastore import DatastoreListModel


class UserWidget(QWidget):
    def __init__(self, parent: QWidget):
        """
        QWidget to display user informations

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "wdg_user.ui"), self)
        self.gui_utils = GuiCommonUtils()

        self.mdl_datastore = DatastoreListModel(self)
        self.tbv_datastore.setModel(self.mdl_datastore)

        self.gui_utils.make_qlabel_copiable(self.lbl_id_value, self.lbl_id)

    def set_user(self, user: User) -> None:
        """
        Define displayed user

        Args:
            user: (User) displayed user
        """
        self.lne_first_name.setText(user.first_name)
        self.lne_last_name.setText(user.last_name)
        self.lne_email.setText(user.email)
        self.lne_registration_date.setText(user.creation_as_localized_datetime)
        self.lbl_id_value.setText(user._id)
