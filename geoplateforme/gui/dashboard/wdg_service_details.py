import os

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QWidget

from geoplateforme.api.offerings import Offering, OfferingStatus
from geoplateforme.toolbelt import PlgLogger


class ServiceDetailsWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        """
        QWidget to display report for an upload

        Args:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_service_details.ui"),
            self,
        )

        self.setWindowTitle(self.tr("Details"))

        self._offering = None

    def set_offering(self, offering: Offering) -> None:
        """
        Define displayed offering

        Args:
            offering: Offering
        """
        self._offering = offering
        self._set_offering_details(offering)

    def _set_offering_details(self, offering: Offering) -> None:
        """
        Define offering details

        Args:
            offering: (Offering)
        """
        status = offering.status
        self.lbl_status_icon.setText("")
        self.lbl_status_icon.setPixmap(self._get_status_icon(status))
        self.lbl_status.setText(self._get_status_text(offering))

        self.lne_name.setText(offering.layer_name)
        self.lne_id.setText(offering._id)

    def _get_status_text(self, offering: Offering) -> str:
        """
        Define status text from an offering

        Args:
            offering: (Offering) offering

        Returns: status text

        """
        status = offering.status
        if status == OfferingStatus.PUBLISHING:
            result = self.tr("Publication en cours.")
        elif status == OfferingStatus.MODIFYING:
            result = self.tr("Publication en cours de modification.")
        elif status == OfferingStatus.PUBLISHED:
            result = self.tr("Publication réussie.")
        elif status == OfferingStatus.UNPUBLISHING:
            result = self.tr("Dépublication en cours.")
            result += self.tr(
                " You will find above technical information about processing executed and encountered "
                "problem."
            )
        elif status == OfferingStatus.UNSTABLE:
            result = self.tr("Publication instable.")
        else:
            result = ""
        return result

    @staticmethod
    def _get_status_icon(status: OfferingStatus) -> QPixmap:
        """
        Get status icon

        Args:
            status: UploadStatus

        Returns: QPixmap

        """
        if status == OfferingStatus.PUBLISHING:
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == OfferingStatus.MODIFYING:
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == OfferingStatus.UNSTABLE:
            result = QIcon(QgsApplication.iconPath("mIconWarning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == OfferingStatus.MODIFYING:
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        else:
            # PUBLISHED
            result = QIcon(QgsApplication.iconPath("mIconSuccess.svg")).pixmap(
                QSize(16, 16)
            )

        return result
