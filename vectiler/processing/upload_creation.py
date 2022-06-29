import json

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterCrs,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QByteArray, QCoreApplication

from vectiler.api.upload import UploadRequestManager
from vectiler.api.user import UserRequestsManager


class UploadCreationAlgorithm(QgsProcessingAlgorithm):
    DATASTORE = "DATASTORE"
    NAME = "NAME"
    DESCRIPTION = "DESCRIPTION"
    INPUT_LAYERS = "INPUT_LAYERS"
    SRS = "SRS"
    CREATED_UPLOAD_ID = "CREATED_UPLOAD_ID"

    def tr(self, string):
        return QCoreApplication.translate(
            "Create an upload for IGN Geotuileur platform", string
        )

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
        return ""

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterString(
                name=self.DATASTORE,
                description=self.tr("Upload datastore"),
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.NAME,
                description=self.tr("Upload name"),
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.DESCRIPTION,
                description=self.tr("Upload description"),
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                name=self.INPUT_LAYERS,
                layerType=QgsProcessing.TypeVectorAnyGeometry,
                description=self.tr("Uploaded layers"),
                optional=True,
            )
        )

        self.addParameter(QgsProcessingParameterCrs(self.SRS, self.tr("SRS")))

    def processAlgorithm(self, parameters, context, feedback):
        name = self.parameterAsString(parameters, self.NAME, context)
        description = self.parameterAsString(parameters, self.DESCRIPTION, context)
        layers = self.parameterAsLayerList(parameters, self.INPUT_LAYERS, context)
        srs = self.parameterAsCrs(parameters, self.SRS, context)

        datastore = self.parameterAsString(parameters, self.DATASTORE, context)
        upload_id = ""
        if not datastore:
            datastore = self.get_default_datastore(feedback)
        if datastore:
            try:
                manager = UploadRequestManager()

                # Create upload
                upload = manager.create_upload(
                    datastore=datastore, name=name, description=description, srs=srs
                )

                # Add layers file
                for layer in layers:
                    filename = layer.dataProvider().dataSourceUri()
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
        else:
            raise QgsProcessingException("Can't define used datastore")

        return {self.CREATED_UPLOAD_ID: upload_id, self.DATASTORE: datastore}

    def get_default_datastore(self, feedback: QgsProcessingFeedback) -> str:
        datastore = ""
        try:
            manager = UserRequestsManager()
            user = manager.get_user()

            datastore_list = user.get_datastore_list()
            if len(datastore_list) != 0:
                datastore = datastore_list[0].id

        except UserRequestsManager.UnavailableUserException as exc:
            feedback.reportError(self.tr(f"Error while getting user datastore: {exc}"))
        return datastore
