# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

# plugin
from geoplateforme.__about__ import DIR_PLUGIN_ROOT


class IpFilterTableWidget(QWidget):
    def __init__(self, parent: QWidget):
        """
        QWidget to define user key Ip filter

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_ip_filter_table.ui"), self
        )

        # Table widget for iplist
        self.tbw_list.setColumnCount(1)
        self.tbw_list.setHorizontalHeaderLabels([self.tr("IP")])
        self.tbw_list.verticalHeader().setVisible(False)
        self.tbw_list.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.btn_add.clicked.connect(self._add_ip)

        self.btn_del.setIcon(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/icons/Supprimer.svg"))
        )
        self.btn_del.clicked.connect(self._del_selected_item)
        self.btn_del.setEnabled(False)

        self.tbw_list.itemSelectionChanged.connect(self._update_delete_button_state)

    def _update_delete_button_state(self):
        """Enable delete button if at least one row is selected."""
        selected_rows = {item.row() for item in self.tbw_list.selectedItems()}
        self.btn_del.setEnabled(bool(selected_rows))

    def _add_ip(self) -> None:
        """Add ip to whitelist"""
        ip_cidr = self.lne_ip.text()
        self._add_ip_item(ip_cidr)

    def _add_ip_item(self, ip_cidr: str) -> None:
        """Add an IP to blacklist table widget

        :param ip_cidr: ip to add
        :type ip_cidr: str
        """
        row = self.tbw_list.rowCount()
        self.tbw_list.insertRow(row)
        self.tbw_list.setItem(row, 0, QTableWidgetItem(ip_cidr))

    def _del_selected_item(self) -> None:
        rows = [x.row() for x in self.tbw_list.selectedIndexes()]
        rows.sort(reverse=True)
        for row in rows:
            self.tbw_list.removeRow(row)

    def get_ip_list(self) -> list[str]:
        """Get IP list

        :return: ip list
        :rtype: list[str]
        """
        return [
            self.tbw_list.item(row, 0).text() for row in range(self.tbw_list.rowCount())
        ]

    def set_ip_list(self, ip_list: list[str]) -> None:
        """Set ip list value

        :param ip_list: ip values
        :type ip_list: list[str]
        """
        for ip_cidr in ip_list:
            self._add_ip_item(ip_cidr=ip_cidr)
