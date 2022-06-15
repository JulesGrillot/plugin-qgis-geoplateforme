import json

from PyQt5.QtCore import QCoreApplication, QByteArray
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterString,
    QgsProcessingParameterCrs,
    QgsProcessingFeedback
)

from vectiler.api.client import NetworkRequestsManager
from vectiler.api.upload import UploadRequestManager


class UploadCreationAlgorithm(QgsProcessingAlgorithm):
    DATASTORE = "DATASTORE"
    NAME = "NAME"
    DESCRIPTION = "DESCRIPTION"
    INPUT_LAYERS = "INPUT_LAYERS"
    SRS = "SRS"
    CREATED_UPLOAD_ID = "CREATED_UPLOAD_ID"

    def tr(self, string):
        return QCoreApplication.translate("Create an upload for IGN Geotuileur platform", string)

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
                upload = manager.create_upload(datastore=datastore, name=name, description=description, srs=srs)

                # Add layers file
                for layer in layers:
                    filename = layer.dataProvider().dataSourceUri()
                    manager.add_file_with_requests(datastore=datastore, upload=upload.id, filename=filename)

                # Close upload
                manager.close_upload(datastore=datastore, upload=upload.id)

                # Get create upload id
                upload_id = upload.id
            except UploadRequestManager.UploadCreationException as exc:
                feedback.reportError(f"Upload creation failed : {exc}")
            except UploadRequestManager.FileUploadException as exc:
                feedback.reportError(f"File upload failed : {exc}")
            except UploadRequestManager.UploadClosingException as exc:
                feedback.reportError(f"Upload closing failed : {exc}")
        else:
            feedback.reportError(f"Can't define used datastore")

        return {self.CREATED_UPLOAD_ID: upload_id, self.DATASTORE: datastore}

    def get_default_datastore(self, feedback: QgsProcessingFeedback) -> str:
        datastore = ""
        network_requests_manager = NetworkRequestsManager()
        check = network_requests_manager.get_user_info()
        if isinstance(check, (dict, QByteArray, bytes)):
            # decode token as dict
            data = json.loads(check.data().decode("utf-8"))
            if not isinstance(data, dict):
                feedback.reportError(self.tr(f"Invalid user data received. Expected dict, not {type(data)}"))
            else:
                # For now, not using any User object : will be done later
                communities_member = data["communities_member"]
                if len(communities_member) != 0:
                    community = communities_member[0]["community"]
                    datastore = community["datastore"]
        return datastore
