import os

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import QtCore, QtGui, uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QDialog, QMessageBox

# Plugin
from geotuileur.api.user import UserRequestsManager
from geotuileur.toolbelt.preferences import PlgOptionsManager


class AuthenticationDialog(QDialog):
    def __init__(self, parent=None):
        """
        Dialog to define current geotuileur connection as authentication config

        Args:
            parent: parent QObject
        """
        super().__init__(parent)
        self.plg_settings = PlgOptionsManager()

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dlg_authentication.ui"), self
        )

        rx = QtCore.QRegExp("[a-z-A-Z-0-9-_.@]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lbl_userEdit.setValidator(validator)

        # Click and Open URl
        self.clb_url.clicked.connect(lambda: self.openUrl())
        self.clb_forgot.clicked.connect(lambda: self.openUrl())

        self.btn_connection.clicked.connect(self.connect)

    def openUrl(self) -> None:
        QDesktopServices.openUrl(QUrl(str("https://qlf-portail-gpf-beta.ign.fr")))

    def connect(self) -> None:
        """
        Check connection parameter and define current vectiler authentication config
        if connection is valid.

        """
        user = self.lbl_userEdit.text()
        password = self.ple_mdpEdit.text()

        plg_settings = self.plg_settings.get_plg_settings()

        # Create new authentication config and add it to manager
        managerAU = QgsApplication.authManager()
        newAU = plg_settings.create_auth_config(user, password)
        managerAU.storeAuthenticationConfig(newAU, True)

        # If connection valid, remove previous config and use new created config, otherwise remove created config
        if self.check_connection(newAU.id()):
            if plg_settings.qgis_auth_id:
                managerAU.removeAuthenticationConfig(plg_settings.qgis_auth_id)
            plg_settings.qgis_auth_id = newAU.id()
            self.plg_settings.save_from_object(plg_settings)

            # Validate dialog
            self.accept()
        else:
            managerAU.removeAuthenticationConfig(newAU.id())

    def check_connection(self, qgis_auth_id: str) -> bool:
        """
        Check if connection is valid for a qgis authentication id.
        Display a message box with user name and last name if connection valid, or
        message with error message otherwise.

        Args:
            qgis_auth_id: qgis authentication id to use

        Returns: True if connection is valid for qgis_auth_id, False otherwise

        """
        res = True

        # Check connection to API by getting user information
        try:
            manager = UserRequestsManager()
            manager.plg_settings.qgis_auth_id = qgis_auth_id
            user = manager.get_user()

            QMessageBox.information(
                self,
                self.tr("Welcome"),
                self.tr(f"Welcome {user.first_name} {user.last_name} !"),
            )

        except UserRequestsManager.UnavailableUserException as exc:
            QMessageBox.warning(
                self,
                self.tr("Invalid connection"),
                self.tr(f"Invalid connection parameters : {exc}"),
            )
            res = False

        return res
