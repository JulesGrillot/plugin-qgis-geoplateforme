from qgis.PyQt.QtCore import QModelIndex, QObject, Qt
from qgis.PyQt.QtGui import QStandardItemModel

from geoplateforme.api.custom_exceptions import ReadUserPermissionException
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

    def refresh(self) -> None:
        """Refresh QStandardItemModel data with user permission list"""
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
                    print(f"{offering=}")
                    self.setData(
                        self.index(row, self.SERVICE_TYPE), offering.type.value
                    )

        except ReadUserPermissionException as exc:
            self.log(
                f"Error while getting user permissions: {exc}",
                log_level=2,
                push=False,
            )
