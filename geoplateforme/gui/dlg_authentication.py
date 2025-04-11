#! python3  # noqa: E265

"""
Authentication dialog logic.
"""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QDialog

from geoplateforme.api.client import NetworkRequestsManager

# Plugin
from geoplateforme.api.custom_exceptions import InvalidToken, UnavailableUserException
from geoplateforme.api.user import UserRequestsManager
from geoplateforme.gui.lne_validators import email_qval
from geoplateforme.toolbelt import PlgLogger, PlgOptionsManager


class AuthenticationDialog(QDialog):
    def __init__(self, parent=None):
        """Dialog to define current geoplateforme connection as authentication config.

        :param parent: parent widget, defaults to None
        :type parent: QObject, optional
        """
        # init module and ui
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "{}.ui".format(Path(__file__).stem), self)

        # toolbelt
        self.log = PlgLogger().log
        self.plg_settings_mngr = PlgOptionsManager()
        self.plg_settings = self.plg_settings_mngr.get_plg_settings()

        # enforce email input
        self.lne_user_email.setValidator(email_qval)

        # widgets connect
        self.btn_log_in.clicked.connect(self.connect)
        self.btn_forgotten_password.clicked.connect(
            partial(
                QDesktopServices.openUrl, QUrl(self.plg_settings.url_forgotten_password)
            )
        )
        self.btn_sign_in.clicked.connect(
            partial(QDesktopServices.openUrl, QUrl(self.plg_settings.url_sign_in))
        )

    def connect(self) -> None:
        """Check connection parameter and define current geoplateforme authentication config
        if connection is valid.
        """
        # Retrieve form data
        user = self.lne_user_email.text()
        password = self.ple_user_password.text()

        # Create new authentication config and add it to manager
        auth_manager = QgsApplication.authManager()
        new_auth = self.plg_settings.create_auth_config(user, password)
        auth_manager.storeAuthenticationConfig(new_auth, True)
        self.log(
            message="Credentials saved into QGIS Authentication Manager as "
            f" {new_auth.name()} ({new_auth.id()})",
            log_level=4,
        )

        # If connection valid, remove previous config and use new created config,
        # otherwise remove created config
        if self.check_connection(new_auth.id()):
            if self.plg_settings.qgis_auth_id:
                auth_manager.removeAuthenticationConfig(self.plg_settings.qgis_auth_id)
            self.plg_settings.qgis_auth_id = new_auth.id()
            self.plg_settings_mngr.save_from_object(self.plg_settings)

            # Validate dialog
            self.accept()
        else:
            auth_manager.removeAuthenticationConfig(new_auth.id())

    def check_connection(self, qgis_auth_id: str) -> bool:
        """Check if connection is valid for a qgis authentication id.
        Display a message box with user name and last name if connection valid, or
        message with error message otherwise.

        :param qgis_auth_id: qgis authentication id to use
        :type qgis_auth_id: str

        :return: True if connection is valid for qgis_auth_id, False otherwise
        :rtype: bool
        """
        res = True

        # Check connection to API by getting token user information
        try:
            network_manager = NetworkRequestsManager()
            network_manager.plg_settings.qgis_auth_id = qgis_auth_id
            network_manager.get_api_token()

            manager = UserRequestsManager()
            manager.plg_settings.qgis_auth_id = qgis_auth_id
            user = manager.get_user()

            self.log(
                message=self.tr(f"Welcome {user.first_name} {user.last_name}!"),
                log_level=3,
                push=True,
                duration=5,
            )

        except (UnavailableUserException, InvalidToken) as exc:
            self.log(
                message=self.tr(f"Invalid connection parameters: {exc}"),
                log_level=2,
                push=True,
                duration=30,
            )
            res = False

        return res
