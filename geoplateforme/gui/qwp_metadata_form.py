# standard
import os
import re

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage

from geoplateforme.api.custom_exceptions import (
    ReadMetadataException,
    UnavailableMetadataFileException,
)
from geoplateforme.api.metadata import Metadata, MetadataFields, MetadataRequestManager
from geoplateforme.gui.metadata.wdg_metadata_details import MetadataDetailsWidget
from geoplateforme.toolbelt.preferences import PlgOptionsManager


class MetadataFormPageWizard(QWizardPage):
    def __init__(
        self,
        datastore_id: str,
        dataset_name: str,
        parent=None,
    ):
        """
        QWizardPage to define current geoplateforme metadata

        Args:
            parent: parent None
            datastore_id: datastore id
            dataset_name: dataset name
        """

        super().__init__(parent)
        self.setTitle(self.tr("Update or create metadata"))

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_metadata_form.ui"), self
        )

        metadatas = []
        self.new_metadata = True
        manager = MetadataRequestManager()
        tags = {"datasheet_name": dataset_name}
        metadatas = manager._get_metadata_list(datastore_id=datastore_id, tags=tags)
        self.metadata = None
        if len(metadatas) == 1:
            try:
                self.new_metadata = False
                self.metadata = metadatas[0]
                self.wdg_metadata = MetadataDetailsWidget(
                    metadata=self.metadata,
                    datastore_id=datastore_id,
                    creation_mode=True,
                )
                self.wdg_metadata.le_unique_id.setReadOnly(True)
            except UnavailableMetadataFileException as exc:
                self.log(
                    f"Error while getting Metadata informations: {exc}",
                    log_level=2,
                    push=False,
                )
            except ReadMetadataException as exc:
                self.log(
                    f"Error while reading Metadata informations: {exc}",
                    log_level=2,
                    push=False,
                )
        if self.metadata is None:
            self.metadata = Metadata(
                _id="",
                datastore_id=datastore_id,
                is_detailed=True,
                _dataset_name=dataset_name,
            )
            self.metadata._fields = MetadataFields()
            self.wdg_metadata = MetadataDetailsWidget(
                metadata=self.metadata, datastore_id=datastore_id, creation_mode=True
            )
        self.gridLayout.addWidget(self.wdg_metadata)

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        valid = True
        mandatory_fields = [
            {
                "field": self.wdg_metadata.le_title,
                "not_valid": len(self.wdg_metadata.le_title.text()) == 0,
            },
            {
                "field": self.wdg_metadata.te_description,
                "not_valid": len(self.wdg_metadata.te_description.toPlainText()) == 0,
            },
            {
                "field": self.wdg_metadata.tb_thematics,
                "not_valid": len(self.wdg_metadata.tb_thematics.tags) == 0,
            },
            {
                "field": self.wdg_metadata.le_contact_email,
                "not_valid": len(self.wdg_metadata.le_contact_email.text()) == 0,
            },
            {
                "field": self.wdg_metadata.le_unique_id,
                "not_valid": len(
                    re.findall(
                        r"^[A-Za-z_][A-Za-z0-9_.-]*$",
                        self.wdg_metadata.le_unique_id.text(),
                    )
                )
                == 0,
            },
            {
                "field": self.wdg_metadata.le_org_name,
                "not_valid": len(self.wdg_metadata.le_org_name.text()) == 0,
            },
            {
                "field": self.wdg_metadata.le_org_email,
                "not_valid": len(self.wdg_metadata.le_org_email.text()) == 0,
            },
            {
                "field": self.wdg_metadata.de_creation_date,
                "not_valid": self.wdg_metadata.de_creation_date.date()
                == self.wdg_metadata.de_creation_date.minimumDate(),
            },
        ]
        for field in mandatory_fields:
            if field["not_valid"]:
                field["field"].setStyleSheet("border: 1px solid red;")
                valid = False
            else:
                field["field"].setStyleSheet("border: 1px solid grey;")

        if valid is False:
            QMessageBox.warning(
                self,
                self.tr("Missing informations."),
                self.tr("Please fill all fields."),
            )

        sandbox_datastore_ids = (
            PlgOptionsManager.get_plg_settings().sandbox_datastore_ids
        )
        if valid:
            if (
                self.metadata.datastore_id in sandbox_datastore_ids
                and not self.wdg_metadata.le_unique_id.text()
                .upper()
                .startswith("SANDBOX")
            ):
                self.wdg_metadata.le_unique_id.setText(
                    f"SANDBOX.{self.wdg_metadata.le_unique_id.text()}"
                )
            self.wdg_metadata.update_metadata_fields()
        return valid
