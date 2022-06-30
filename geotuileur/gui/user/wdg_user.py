import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

from geotuileur.api.user import User
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

        self.mdl_datastore = DatastoreListModel(self)
        self.tbv_datastore.setModel(self.mdl_datastore)

    def set_user(self, user: User) -> None:
        """
        Define displayed user

        Args:
            user: (User) displayed user
        """
        self.lne_first_name.setText(user.first_name)
        self.lne_last_name.setText(user.last_name)
        self.lne_email.setText(user.email)
        self.lne_registration_date.setText(user.creation)
        self.lne_id.setText(user._id)
