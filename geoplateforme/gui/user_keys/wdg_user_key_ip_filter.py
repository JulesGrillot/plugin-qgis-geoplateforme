# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

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

        # Table widget for whitelist
        self.tbw_whitelist.setColumnCount(1)
        self.tbw_whitelist.setHorizontalHeaderLabels([self.tr("IP")])
        self.tbw_whitelist.verticalHeader().setVisible(False)
        self.tbw_whitelist.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Table widget for blacklist
        self.tbw_blacklist.setColumnCount(1)
        self.tbw_blacklist.setHorizontalHeaderLabels([self.tr("IP")])
        self.tbw_blacklist.verticalHeader().setVisible(False)
        self.tbw_blacklist.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Connection for whitelist and blacklist add
        self.btn_add_whitelist.clicked.connect(self._add_whitelist)
        self.btn_add_blacklist.clicked.connect(self._add_blacklist)

        # Update display page with radiobutton
        self.rbtn_no_filter.toggled.connect(self._filter_type_updated)
        self.rbtn_whitelist.toggled.connect(self._filter_type_updated)
        self.rbtn_blacklist.toggled.connect(self._filter_type_updated)

    def _filter_type_updated(self) -> None:
        """Change displayed page when filter type is changed"""
        if self.rbtn_no_filter.isChecked():
            self.stack_filter.setCurrentWidget(self.page_no_filter)
        elif self.rbtn_whitelist.isChecked():
            self.stack_filter.setCurrentWidget(self.page_whitelist)
        else:
            self.stack_filter.setCurrentWidget(self.page_blacklist)

    def _add_whitelist(self) -> None:
        """Add ip to whitelist"""
        ip_cidr = self.lne_whitelist.text()
        self._add_whitelist_item(ip_cidr)

    def _add_whitelist_item(self, ip_cidr: str) -> None:
        """Add an IP to blacklist table widget

        :param ip_cidr: ip to add
        :type ip_cidr: str
        """
        row = self.tbw_whitelist.rowCount()
        self.tbw_whitelist.insertRow(row)
        self.tbw_whitelist.setItem(row, 0, QTableWidgetItem(ip_cidr))

    def _add_blacklist(self) -> None:
        """Add ip to blacklist"""
        ip_cidr = self.lne_blacklist.text()
        self._add_blacklist_item(ip_cidr)

    def _add_blacklist_item(self, ip_cidr: str) -> None:
        """Add an IP to blacklist table widget

        :param ip_cidr: ip to add
        :type ip_cidr: str
        """
        row = self.tbw_blacklist.rowCount()
        self.tbw_blacklist.insertRow(row)
        self.tbw_blacklist.setItem(row, 0, QTableWidgetItem(ip_cidr))

    def get_blacklist(self) -> Optional[list[str]]:
        """Get blacklist IP if option selected

        :return: blacklist IP if option selected, None otherwise
        :rtype: Optional[list[str]]
        """
        if self.rbtn_blacklist.isChecked():
            return [
                self.tbw_blacklist.item(row, 0).text()
                for row in range(self.tbw_blacklist.rowCount())
            ]
        return None

    def set_blacklist(self, blacklist: Optional[list[str]]) -> None:
        """Set blacklist ip value

        :param blacklist: blacklist ip values
        :type blacklist: Optional[list[str]]
        """
        if blacklist:
            for ip_cidr in blacklist:
                self._add_blacklist_item(ip_cidr=ip_cidr)

    def get_whitelist(self) -> Optional[list[str]]:
        """Get whitelist IP if option selected

        :return: whitelist IP if option selected, None otherwise
        :rtype: Optional[list[str]]
        """
        if self.rbtn_whitelist.isChecked():
            return [
                self.tbw_whitelist.item(row, 0).text()
                for row in range(self.tbw_whitelist.rowCount())
            ]
        return None

    def set_whitelist(self, whitelist: Optional[list[str]]) -> None:
        """Set whitelist ip value

        :param whitelist: whitelist ip values
        :type whitelist: Optional[list[str]]
        """
        if whitelist:
            for ip_cidr in whitelist:
                self._add_whitelist_item(ip_cidr=ip_cidr)
