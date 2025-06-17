# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QAbstractItemView, QHeaderView, QWidget

# plugin
from geoplateforme.gui.user_keys.mdl_user_permissions import UserPermissionListModel
from geoplateforme.processing.provider import GeoplateformeProvider
from geoplateforme.processing.user_key.create_basic_key import CreateBasicKeyAlgorithm
from geoplateforme.processing.user_key.create_hash_key import CreateHashKeyAlgorithm
from geoplateforme.processing.user_key.create_oauth_key import CreateOAuthKeyAlgorithm


class UserKeyCreationWidget(QWidget):
    def __init__(self, parent: QWidget):
        """
        QWidget to create user key

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_user_key_creation.ui"), self
        )

        # Model for permission
        self.mdl_user_permission = UserPermissionListModel(parent=self, checkable=True)
        self.mdl_user_permission.refresh()

        self.tbv_permissions.setModel(self.mdl_user_permission)
        self.tbv_permissions.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tbv_permissions.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbv_permissions.verticalHeader().setVisible(False)

        # Update display page with radiobutton
        self.rbtn_basic.toggled.connect(self._key_type_updated)
        self.rbtn_hash.toggled.connect(self._key_type_updated)
        self.rbtn_oauth.toggled.connect(self._key_type_updated)

    def _key_type_updated(self) -> None:
        """Change displayed page when key type is changed"""
        if self.rbtn_basic.isChecked():
            self.stack_key.setCurrentWidget(self.page_basic)
        elif self.rbtn_hash.isChecked():
            self.stack_key.setCurrentWidget(self.page_hash)
        else:
            self.stack_key.setCurrentWidget(self.page_oauth)

    def get_creation_parameters(self) -> dict:
        """Get algorithm parameters for user key creation

        :return: user key creation algorithm parameters
        :rtype: dict
        """
        if self.rbtn_basic.isChecked():
            return {
                CreateBasicKeyAlgorithm.NAME: self.lne_name.text(),
                CreateBasicKeyAlgorithm.WHITELIST: self.wdg_user_key_ip_filter.get_whitelist(),
                CreateBasicKeyAlgorithm.BLACKLIST: self.wdg_user_key_ip_filter.get_blacklist(),
                CreateBasicKeyAlgorithm.USER_AGENT: self.lne_user_agent.text(),
                CreateBasicKeyAlgorithm.REFERER: self.lne_referer.text(),
                CreateBasicKeyAlgorithm.LOGIN: self.lne_login.text(),
                CreateBasicKeyAlgorithm.PASSWORD: self.lne_password.text(),
            }
        elif self.rbtn_hash.isChecked():
            return {
                CreateHashKeyAlgorithm.NAME: self.lne_name.text(),
                CreateHashKeyAlgorithm.WHITELIST: self.wdg_user_key_ip_filter.get_whitelist(),
                CreateHashKeyAlgorithm.BLACKLIST: self.wdg_user_key_ip_filter.get_blacklist(),
                CreateHashKeyAlgorithm.USER_AGENT: self.lne_user_agent.text(),
                CreateHashKeyAlgorithm.REFERER: self.lne_referer.text(),
            }
        return {
            CreateOAuthKeyAlgorithm.NAME: self.lne_name.text(),
            CreateOAuthKeyAlgorithm.WHITELIST: self.wdg_user_key_ip_filter.get_whitelist(),
            CreateOAuthKeyAlgorithm.BLACKLIST: self.wdg_user_key_ip_filter.get_blacklist(),
            CreateOAuthKeyAlgorithm.USER_AGENT: self.lne_user_agent.text(),
            CreateOAuthKeyAlgorithm.REFERER: self.lne_referer.text(),
        }

    def get_creation_algo_str(self) -> str:
        """Get algorithm name for user key creation

        :return: algorithm name
        :rtype: str
        """
        if self.rbtn_basic.isChecked():
            return f"{GeoplateformeProvider().id()}:{CreateBasicKeyAlgorithm().name()}"
        elif self.rbtn_hash.isChecked():
            return f"{GeoplateformeProvider().id()}:{CreateHashKeyAlgorithm().name()}"
        return f"{GeoplateformeProvider().id()}:{CreateOAuthKeyAlgorithm().name()}"
