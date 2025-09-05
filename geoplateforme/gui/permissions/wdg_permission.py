# standard
import os
from typing import Optional

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QDateTime, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QDialogButtonBox,
    QHeaderView,
    QMessageBox,
    QWidget,
)

# plugin
from geoplateforme.__about__ import DIR_PLUGIN_ROOT
from geoplateforme.api.permissions import Permission
from geoplateforme.gui.mdl_offering import OfferingListModel
from geoplateforme.gui.proxy_model_offering import OfferingProxyModel
from geoplateforme.processing.permissions.delete_permission import (
    DeletePermissionAlgorithm,
)
from geoplateforme.processing.permissions.update_permission import (
    UpdatePermissionAlgorithm,
)
from geoplateforme.processing.provider import GeoplateformeProvider


class PermissionWidget(QWidget):
    permission_deleted = pyqtSignal(str)
    permission_updated = pyqtSignal(str)

    def __init__(self, parent: QWidget):
        """
        QWidget to create permission

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "wdg_permission.ui"), self)

        self.datastore_id = None

        # Model for offering
        self.mdl_offering = OfferingListModel(parent=self, checkable=True)
        self.proxy_mdl_offering = OfferingProxyModel(self)
        self.proxy_mdl_offering.setSourceModel(self.mdl_offering)
        self.proxy_mdl_offering.set_open_filter(open_filter=False)

        # Display only name and type in tableview
        self.tbv_offering.setModel(self.proxy_mdl_offering)
        self.tbv_offering.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbv_offering.setColumnHidden(OfferingListModel.ID_COL, True)
        self.tbv_offering.setColumnHidden(OfferingListModel.VISIBILITY_COL, True)
        self.tbv_offering.setColumnHidden(OfferingListModel.STATUS_COL, True)
        self.tbv_offering.setColumnHidden(OfferingListModel.OPEN_COL, True)
        self.tbv_offering.setColumnHidden(OfferingListModel.AVAILABLE_COL, True)
        self.tbv_offering.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbv_offering.verticalHeader().setVisible(False)

        # No end date by default
        self.datetime_end_date.setNullRepresentation(self.tr("Aucune"))
        self.datetime_end_date.setDateTime(QDateTime())

        self.btn_delete.setIcon(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/icons/Supprimer.svg"))
        )
        self.btn_delete.clicked.connect(self.delete_permission)
        self.btn_update.setIcon(
            QIcon(":images/themes/default/mActionToggleEditing.svg")
        )
        self.btn_update.clicked.connect(self._update_permission)
        self.btnbox_update.clicked.connect(self._update_btnbox_clicked)

        self._apply_update_mode(apply=False)

        self._permission = None

    def _update_permission(self) -> None:
        """Update widget to display component for update apply"""
        self._apply_update_mode(apply=True)

    def _apply_update_mode(self, apply: bool) -> None:
        """Update widget to display component if update is apply

        :param apply: apply update mode
        :type apply: bool
        """
        self.btnbox_update.setVisible(apply)
        self.btn_update.setVisible(not apply)
        self.btn_delete.setVisible(not apply)
        self.lne_licence.setReadOnly(not apply)
        self.datetime_end_date.setReadOnly(not apply)

        if apply:
            self.tbv_offering.setEditTriggers(
                QAbstractItemView.EditTrigger.DoubleClicked
                | QAbstractItemView.EditTrigger.EditKeyPressed
                | QAbstractItemView.EditTrigger.AnyKeyPressed
            )
            self.mdl_offering.editable = True
        else:
            self.tbv_offering.setEditTriggers(
                QAbstractItemView.EditTrigger.NoEditTriggers
            )
            self.mdl_offering.editable = False

    def _update_btnbox_clicked(self, button: QAbstractButton) -> None:
        """Cancel update or apply modification

        :param button: button selected by user
        :type button: QAbstractButton
        """
        btn_role = self.btnbox_update.buttonRole(button)
        # Update rejected, restore previous values
        if btn_role == QDialogButtonBox.ButtonRole.RejectRole:
            self._apply_update_mode(apply=False)
            self.set_permission(self._permission)
        # Update accepted, try to update user key
        elif btn_role == QDialogButtonBox.ButtonRole.ApplyRole:
            reply = QMessageBox.question(
                self,
                self.tr("Modification"),
                self.tr("Êtes-vous sûr de vouloir modifier cette permission ?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                params = {
                    UpdatePermissionAlgorithm.DATASTORE_ID: self._permission.datastore_id,
                    UpdatePermissionAlgorithm.PERMISSION_ID: self._permission._id,
                    UpdatePermissionAlgorithm.LICENCE: self.get_licence(),
                    UpdatePermissionAlgorithm.OFFERINGS: ",".join(
                        self.get_offering_ids()
                    ),
                }
                if end_date := self.get_end_date():
                    params[UpdatePermissionAlgorithm.END_DATE] = end_date

                algo_str = f"{GeoplateformeProvider().id()}:{UpdatePermissionAlgorithm().name()}"
                alg = QgsApplication.processingRegistry().algorithmById(algo_str)
                context = QgsProcessingContext()
                feedback = QgsProcessingFeedback()
                _, success = alg.run(
                    parameters=params, context=context, feedback=feedback
                )
                if success:
                    self._apply_update_mode(apply=False)
                    self.permission_updated.emit(self._permission._id)
                else:
                    QMessageBox.critical(
                        self,
                        self.tr("Modification"),
                        self.tr("La permission n'a pas pu être modifiée :\n {}").format(
                            feedback.textLog()
                        ),
                    )

    def delete_permission(self) -> None:
        """Delete current permission"""
        reply = QMessageBox.question(
            self,
            self.tr("Suppression"),
            self.tr("Êtes-vous sûr de vouloir supprimer cette permission ?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            params = {
                DeletePermissionAlgorithm.PERMISSION_ID: self._permission._id,
                DeletePermissionAlgorithm.DATASTORE_ID: self._permission.datastore_id,
            }

            algo_str = (
                f"{GeoplateformeProvider().id()}:{DeletePermissionAlgorithm().name()}"
            )
            alg = QgsApplication.processingRegistry().algorithmById(algo_str)
            context = QgsProcessingContext()
            feedback = QgsProcessingFeedback()
            _, success = alg.run(parameters=params, context=context, feedback=feedback)
            if success:
                self.permission_deleted.emit(self._permission._id)
            else:
                QMessageBox.critical(
                    self,
                    self.tr("Suppression"),
                    self.tr("La permission n'a pas pu être supprimée :\n {}").format(
                        feedback.textLog()
                    ),
                )

    def set_permission(self, permission: Permission) -> None:
        """Define visible permission

        :param permission: permission
        :type permission: Permission
        """
        self._permission = permission
        self.mdl_offering.set_datastore(permission.datastore_id, open_filter=False)
        self.lne_licence.setText(permission.licence)
        if permission.end_date:
            self.datetime_end_date.setDateTime(permission.local_end_date)
        if permission.offerings:
            self.mdl_offering.set_checked_offering(
                [offering._id for offering in permission.offerings]
            )

    def get_licence(self) -> str:
        """Get licence

        :return: licence
        :rtype: str
        """
        return self.lne_licence.text()

    def get_end_date(self) -> Optional[QDateTime]:
        """Get end date if defined

        :return: end date, None if not defined
        :rtype: Optional[QDateTime]
        """
        end_date = self.datetime_end_date.dateTime()
        if not end_date.isNull():
            return end_date
        return None

    def get_offering_ids(self) -> list[str]:
        """Get list of checked offering ids

        :return: checked offering ids
        :rtype: list[str]
        """
        return [
            offering._id
            for offering in self.mdl_offering.get_checked_offering(checked=True)
        ]
