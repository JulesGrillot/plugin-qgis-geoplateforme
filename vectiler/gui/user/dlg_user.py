#! python3  # noqa: E265

"""
    Dialog hosting user information (when logged in).
"""

# standard
import os

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QWidget

# Plugin
from vectiler.api.user import UserRequestsManager
from vectiler.toolbelt import PlgOptionsManager


class UserDialog(QDialog):
    def __init__(self, parent: QWidget):
        """
        Dialog to display current user information and disconnection button

        Args:
            parent: parent QObject

        Args:
            parent:
        """
        super().__init__(parent)
        self.plg_settings = PlgOptionsManager()

        uic.loadUi(os.path.join(os.path.dirname(__file__), "dlg_user.ui"), self)

        self.setWindowTitle(self.tr("User informations"))

        self.btn_disconnect.setIcon(
            QIcon(QgsApplication.iconPath("repositoryUnavailable.svg"))
        )
        self.btn_disconnect.clicked.connect(self._disconnect)

        try:
            manager = UserRequestsManager()
            user = manager.get_user()
            self.wdg_user.set_user(user)
        except UserRequestsManager.UnavailableUserException as exc:
            QMessageBox.warning(
                self,
                self.tr("Unavailable user"),
                self.tr(f"Can't define connected user : {exc}"),
            )

    def _disconnect(self) -> None:
        """
        Disconnect current user and close dialog

        """
        plg_settings = self.plg_settings.get_plg_settings()
        plg_settings.qgis_auth_id = None
        self.plg_settings.save_from_object(plg_settings)
        super().accept()
