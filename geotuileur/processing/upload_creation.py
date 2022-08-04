import json

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFile,
)
from qgis.PyQt.QtCore import QCoreApplication

from geotuileur.api.upload import UploadRequestManager


class UploadCreationAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    NAME = "name"
    DESCRIPTION = "description"
    FILES = "files"
    SRS = "srs"

    CREATED_UPLOAD_ID = "CREATED_UPLOAD_ID"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return UploadCreationAlgorithm()

    def name(self):
        return "upload_creation"

    def displayName(self):
        return self.tr("Create upload")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):
        return self.tr(
            "Create upload in geotuileur platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.DATASTORE}": datastore id (str),\n'
            f'    "{self.NAME}": wanted upload name (str),\n'
            f'    "{self.DESCRIPTION}": upload description (str),\n'
            f'    "{self.FILES}": upload full file path list [str],\n'
            f'    "{self.SRS}": upload SRS (str) must be in IGNF or EPSG repository,\n'
            "}\n"
            f"Returns created upload id in {self.CREATED_UPLOAD_ID} results"
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT_JSON,
                description=self.tr("Input .json file"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        filename = self.parameterAsFile(parameters, self.INPUT_JSON, context)

        with open(filename, "r") as file:
            data = json.load(file)

            name = data[self.NAME]
            description = data[self.DESCRIPTION]
            files = data[self.FILES]
            srs = data[self.SRS]
            datastore = data[self.DATASTORE]

            try:
                manager = UploadRequestManager()

                # Create upload
                upload = manager.create_upload(
                    datastore=datastore, name=name, description=description, srs=srs
                )

                # Add files
                for filename in files:
                    manager.add_file_with_requests(
                        datastore=datastore, upload=upload.id, filename=filename
                    )

                # Close upload
                manager.close_upload(datastore=datastore, upload=upload.id)

                # Get create upload id
                upload_id = upload.id
            except UploadRequestManager.UploadCreationException as exc:
                raise QgsProcessingException(f"Upload creation failed : {exc}")
            except UploadRequestManager.FileUploadException as exc:
                raise QgsProcessingException(f"File upload failed : {exc}")
            except UploadRequestManager.UploadClosingException as exc:
                raise QgsProcessingException(f"Upload closing failed : {exc}")

        return {self.CREATED_UPLOAD_ID: upload_id, self.DATASTORE: datastore}
