from typing import Optional

from qgis.PyQt.QtCore import QObject, Qt
from qgis.PyQt.QtGui import QStandardItemModel

from geoplateforme.api.configuration import (
    Configuration,
    ConfigurationField,
    ConfigurationRequestManager,
)
from geoplateforme.api.custom_exceptions import ReadConfigurationException
from geoplateforme.api.utils import as_datetime
from geoplateforme.toolbelt import PlgLogger


class ConfigurationListModel(QStandardItemModel):
    NAME_COL = 0
    TYPE_COL = 1
    DATE_COL = 2

    def __init__(self, parent: QObject = None):
        """QStandardItemModel for configuration list display

        :param parent: parent
        :type parent: QObject
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels(
            [
                self.tr("Name"),
                self.tr("Type"),
                self.tr("Date"),
            ]
        )

    def set_datastore(
        self, datastore_id: str, dataset_name: Optional[str] = None
    ) -> None:
        """Refresh QStandardItemModel data with current datastore stored data

        :param datastore_id: datastore id
        :type datastore_id: str
        :param dataset_name: dataset name
        :type dataset_name: str, optional
        """
        self.removeRows(0, self.rowCount())

        manager = ConfigurationRequestManager()
        try:
            if dataset_name:
                tags = {"datasheet_name": dataset_name}
                configurations = manager.get_configuration_list(
                    datastore_id=datastore_id,
                    with_fields=[
                        ConfigurationField.NAME,
                        ConfigurationField.LAYER_NAME,
                        ConfigurationField.LAST_EVENT,
                        ConfigurationField.STATUS,
                        ConfigurationField.TYPE,
                    ],
                    tags=tags,
                )
            else:
                configurations = manager.get_configuration_list(
                    datastore_id=datastore_id,
                    with_fields=[
                        ConfigurationField.NAME,
                        ConfigurationField.LAYER_NAME,
                        ConfigurationField.LAST_EVENT,
                        ConfigurationField.STATUS,
                        ConfigurationField.TYPE,
                    ],
                )
            for config in configurations:
                self.insert_configuration(config)
        except ReadConfigurationException as exc:
            self.log(
                f"Error while getting configuration informations: {exc}",
                log_level=2,
                push=False,
            )

    def insert_configuration(self, config: Configuration) -> None:
        """Insert stored data in model

        :param stored_data: stored data to insert
        :type stored_data: StoredData
        """
        row = self.rowCount()
        self.insertRow(row)

        self.setData(self.index(row, self.NAME_COL), config.layer_name)
        self.setData(self.index(row, self.NAME_COL), config, Qt.ItemDataRole.UserRole)
        self.setData(self.index(row, self.TYPE_COL), config.type_data)

        self.setData(
            self.index(row, self.DATE_COL),
            as_datetime(config.get_last_event_date()),
        )
