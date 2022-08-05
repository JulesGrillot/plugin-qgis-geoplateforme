# standard
import os
from functools import partial

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QEvent
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QWidget

# plugin
from geotuileur.api.user import User
from geotuileur.gui.gui_commons import GuiCommonUtils
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
        self.gui_utils = GuiCommonUtils()

        self.mdl_datastore = DatastoreListModel(self)
        self.tbv_datastore.setModel(self.mdl_datastore)

        # show only icon on copy button
        self.btn_copy_id.setText("")
        self.btn_copy_id.setIcon(QIcon(QgsApplication.iconPath("mActionEditCopy.svg")))
        self.btn_copy_id.pressed.connect(
            partial(
                self.gui_utils.copy_widget_txt_to_clipboard,
                wdg_source=self.lbl_id_value,
            )
        )
        self.lbl_id_value.installEventFilter(self)
        self.lbl_id_value.setBuddy(self.lbl_id)

    def eventFilter(self, source: QWidget, event: QEvent) -> bool:
        """Custom event filter to handle special user actions. Can override any widget
        interaction.

        :param source: widget which emitted the event
        :type source: QWidget
        :param event: event type
        :type event: QEvent

        :return: True if event has been handled. Note: retun bool is mandatory.
        :rtype: bool
        """
        if event.type() == QEvent.MouseButtonDblClick:
            self.gui_utils.copy_widget_txt_to_clipboard(source)
            return True
        return False

    def set_user(self, user: User) -> None:
        """
        Define displayed user

        Args:
            user: (User) displayed user
        """
        self.lne_first_name.setText(user.first_name)
        self.lne_last_name.setText(user.last_name)
        self.lne_email.setText(user.email)
        self.lne_registration_date.setText(user.creation_as_localized_datetime)
        self.lbl_id_value.setText(user._id)
