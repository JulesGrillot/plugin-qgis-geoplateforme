# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

# plugin


class UserKeyIpFilterWidget(QWidget):
    def __init__(self, parent: QWidget):
        """
        QWidget to define user key Ip filter

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_user_key_ip_filter.ui"), self
        )

        # Update display page with radiobutton
        self.rbtn_no_filter.toggled.connect(self._filter_type_updated)
        self.rbtn_whitelist.toggled.connect(self._filter_type_updated)
        self.rbtn_blacklist.toggled.connect(self._filter_type_updated)

        self.wdg_ip_blacklist.setVisible(False)
        self.wdg_ip_whitelist.setVisible(False)

    def _filter_type_updated(self) -> None:
        """Change displayed page when filter type is changed"""
        if self.rbtn_no_filter.isChecked():
            self.wdg_ip_blacklist.setVisible(False)
            self.wdg_ip_whitelist.setVisible(False)
        elif self.rbtn_whitelist.isChecked():
            self.wdg_ip_blacklist.setVisible(False)
            self.wdg_ip_whitelist.setVisible(True)
        else:
            self.wdg_ip_blacklist.setVisible(True)
            self.wdg_ip_whitelist.setVisible(False)

    def get_blacklist(self) -> Optional[list[str]]:
        """Get blacklist IP if option selected

        :return: blacklist IP if option selected, None otherwise
        :rtype: Optional[list[str]]
        """
        if self.rbtn_blacklist.isChecked():
            return self.wdg_ip_blacklist.get_ip_list()
        return None

    def set_blacklist(self, blacklist: Optional[list[str]]) -> None:
        """Set blacklist ip value

        :param blacklist: blacklist ip values
        :type blacklist: Optional[list[str]]
        """
        if blacklist:
            self.wdg_ip_blacklist.set_ip_list(blacklist)
            self.rbtn_blacklist.setChecked(True)

    def get_whitelist(self) -> Optional[list[str]]:
        """Get whitelist IP if option selected

        :return: whitelist IP if option selected, None otherwise
        :rtype: Optional[list[str]]
        """
        if self.rbtn_whitelist.isChecked():
            return self.wdg_ip_whitelist.get_ip_list()
        return None

    def set_whitelist(self, whitelist: Optional[list[str]]) -> None:
        """Set whitelist ip value

        :param whitelist: whitelist ip values
        :type whitelist: Optional[list[str]]
        """
        if whitelist:
            self.wdg_ip_whitelist.set_ip_list(whitelist)
            self.rbtn_whitelist.setChecked(True)
