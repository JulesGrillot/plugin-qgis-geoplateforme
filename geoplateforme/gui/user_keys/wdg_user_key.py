# standard
import os
from typing import Tuple

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QAbstractItemView, QHeaderView, QWidget

# plugin
from geoplateforme.api.key_access import KeyAccessRequestManager
from geoplateforme.api.offerings import Offering
from geoplateforme.api.permissions import Permission
from geoplateforme.api.user_key import UserKey, UserKeyType
from geoplateforme.gui.user_keys.mdl_user_permissions import UserPermissionListModel


class UserKeyWidget(QWidget):
    def __init__(self, parent: QWidget):
        """
        QWidget to display user key

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "wdg_user_key.ui"), self)

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

    def set_user_key(self, user_key: UserKey) -> None:
        """Define visible user key

        :param user_key: user key
        :type user_key: UserKey
        """
        self.lne_name.setText(user_key.name)
        if user_key._type == UserKeyType.HASH:
            self.lbl_key_type_description.setText(self.tr("Cette clé est de type HASH"))
            self.gpb_hash.setVisible(True)
            if "hash" in user_key.type_infos:
                self.lne_hash.setText(user_key.type_infos["hash"])
            else:
                self.lne_hash.setText(self.tr("Indisponible"))
        elif user_key._type == UserKeyType.BASIC:
            self.lbl_key_type_description.setText(
                self.tr("Cette clé est de type BASIC")
            )
            self.gpb_hash.setVisible(False)
        else:
            self.lbl_key_type_description.setText(
                self.tr("Cette clé est de type OAuth2")
            )
            self.gpb_hash.setVisible(False)

        self.wdg_user_key_ip_filter.set_blacklist(user_key.blacklist)
        self.wdg_user_key_ip_filter.set_whitelist(user_key.whitelist)
        if user_key.user_agent:
            self.lne_user_agent.setText(user_key.user_agent)
        if user_key.referer:
            self.lne_referer.setText(user_key.referer)

        # Get key accesses
        manager = KeyAccessRequestManager()
        access_key_list = manager.get_key_access_list(user_key_id=user_key._id)

        for key_access in access_key_list:
            self.mdl_user_permission.check_user_key_access(key_access=key_access)

    def get_selected_permission_and_offering(
        self,
    ) -> list[Tuple[Permission, list[Offering]]]:
        """Return permission and offering with wanted checked status

        :param checked: wanted check status, defaults to True
        :type checked: bool, optional
        :return: list of permission and selected offering
        :rtype: list[Tuple[Permission, list[Offering]]]
        """
        return self.mdl_user_permission.get_checked_permission_and_offering(
            checked=True
        )
