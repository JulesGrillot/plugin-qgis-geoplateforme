from typing import Any, Tuple

from qgis.PyQt.QtCore import QModelIndex, QObject, Qt
from qgis.PyQt.QtGui import QStandardItemModel

from geoplateforme.api.custom_exceptions import ReadUserPermissionException
from geoplateforme.api.key_access import KeyAccess
from geoplateforme.api.offerings import Offering
from geoplateforme.api.permissions import Permission
from geoplateforme.api.user_permission import UserPermissionRequestManager
from geoplateforme.toolbelt import PlgLogger


class UserPermissionListModel(QStandardItemModel):
    LICENCE_COL = 0
    SERVICE = 1
    SERVICE_TYPE = 2

    def __init__(self, parent: QObject = None, checkable: bool = False):
        """QStandardItemModel for user permissions list display

        :param parent: parent
        :type parent: QObject
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels(
            [
                self.tr("Licence"),
                self.tr("Service"),
                self.tr("Type"),
            ]
        )
        self._checkable = checkable
        self.editable = True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Define flags for model

        :param index: model index
        :type index: QModelIndex
        :return: item flags
        :rtype: Qt.ItemFlags
        """
        # All item are enabled and selectable
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == self.LICENCE_COL and self._checkable:
            flags = flags | Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> bool:
        """
        Override QStandardItemModel setData to disable edition.

        Args:
            index: QModelIndex
            value: new value
            role: Qt role

        Returns: True if data set, False otherwise

        """
        if not self.editable:
            return False

        return super().setData(index, value, role)

    def refresh(self) -> None:
        """Refresh QStandardItemModel data with user permission list"""
        prev_editable = self.editable
        self.editable = True
        self.removeRows(0, self.rowCount())
        try:
            manager = UserPermissionRequestManager()
            permissions = manager.get_user_permission_list()

            for permission in permissions:
                for offering in permission.offerings:
                    self.insertRow(self.rowCount())
                    row = self.rowCount() - 1
                    self.setData(self.index(row, self.LICENCE_COL), permission.licence)
                    self.setData(
                        self.index(row, self.LICENCE_COL),
                        permission,
                        Qt.ItemDataRole.UserRole,
                    )
                    if self._checkable:
                        self.setData(
                            self.index(row, self.LICENCE_COL),
                            Qt.CheckState.Unchecked,
                            Qt.ItemDataRole.CheckStateRole,
                        )

                    self.setData(self.index(row, self.SERVICE), offering.layer_name)
                    self.setData(
                        self.index(row, self.SERVICE),
                        offering,
                        Qt.ItemDataRole.UserRole,
                    )
                    self.setData(
                        self.index(row, self.SERVICE_TYPE), offering.type.value
                    )

        except ReadUserPermissionException as exc:
            self.log(
                f"Error while getting user permissions: {exc}",
                log_level=2,
                push=False,
            )
        self.editable = prev_editable

    def check_user_key_access(self, key_access: KeyAccess) -> None:
        """Check offering for a key access

        :param key_access: key access
        :type key_access: KeyAccess
        """
        prev_editable = self.editable
        self.editable = True
        for row in range(self.rowCount()):
            permission = self.data(
                self.index(row, self.LICENCE_COL), Qt.ItemDataRole.UserRole
            )
            offering = self.data(
                self.index(row, self.SERVICE), Qt.ItemDataRole.UserRole
            )
            if (
                permission._id == key_access.permission._id
                and offering._id == key_access.offering._id
            ):
                self.setData(
                    self.index(row, self.LICENCE_COL),
                    Qt.CheckState.Checked,
                    Qt.ItemDataRole.CheckStateRole,
                )
                break
        self.editable = prev_editable

    def get_checked_permission_and_offering(
        self, checked: bool = True
    ) -> list[Tuple[Permission, list[Offering]]]:
        """Return permission and offering with wanted checked status

        :param checked: wanted check status, defaults to True
        :type checked: bool, optional
        :return: list of permission and selected offering
        :rtype: list[Tuple[Permission, list[Offering]]]
        """
        result = []
        current_permission = None
        current_permission_offering_list = []
        for row in range(self.rowCount()):
            row_checked = (
                self.data(
                    self.index(row, self.LICENCE_COL), Qt.ItemDataRole.CheckStateRole
                )
                == Qt.CheckState.Checked
            )
            if row_checked == checked:
                permission = self.data(
                    self.index(row, self.LICENCE_COL), Qt.ItemDataRole.UserRole
                )
                offering = self.data(
                    self.index(row, self.SERVICE), Qt.ItemDataRole.UserRole
                )

                # Check if a permission was already found
                if current_permission is None:
                    # Define current permission
                    current_permission = permission

                if current_permission != permission:
                    result.append(
                        (current_permission, current_permission_offering_list)
                    )
                    current_permission = permission
                    current_permission_offering_list = []

                current_permission_offering_list.append(offering)
        if current_permission:
            result.append((current_permission, current_permission_offering_list))

        return result
