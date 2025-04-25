# standard
from time import sleep

# PyQGIS
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFile,
    QgsProcessingParameterMatrix,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# plugin
from geoplateforme.api.custom_exceptions import (
    FileUploadException,
    UnavailableUploadException,
    UploadClosingException,
    UploadCreationException,
)
from geoplateforme.api.upload import UploadRequestManager, UploadStatus
from geoplateforme.processing.utils import tags_from_qgs_parameter_matrix_string
from geoplateforme.toolbelt import PlgOptionsManager


class UploadCreationProcessingFeedback(QgsProcessingFeedback):
    """
    Implementation of QgsProcessingFeedback to store information from processing:
        - created_upload_id (str) : created upload id
    """

    created_upload_id: str = ""


class GpfUploadFromFileAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    NAME = "name"
    DESCRIPTION = "description"
    FILES = "files"
    SRS = "srs"
    TAGS = "tags"

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
        return GpfUploadFromFileAlgorithm()

    def name(self):
        return "upload_from_files"

    def displayName(self):
        return self.tr("Création livraison depuis des fichiers")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):
        return self.tr(
            "Create upload in geoplateforme platform.\n"
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
            QgsProcessingParameterString(
                name=self.DATASTORE,
                description=self.tr("Identifiant de l'entrepôt"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.NAME,
                description=self.tr("Nom de la livraison"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.DESCRIPTION,
                description=self.tr("Description de la livraison"),
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.FILES,
                description=self.tr("Fichier à importer"),
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(self.SRS, self.tr("Système de coordonnées"))
        )

        self.addParameter(
            QgsProcessingParameterMatrix(
                name=self.TAGS,
                description=self.tr("Tags"),
                headers=[self.tr("Tag"), self.tr("Valeur")],
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        name = self.parameterAsString(parameters, self.NAME, context)
        description = self.parameterAsString(parameters, self.DESCRIPTION, context)
        datastore = self.parameterAsString(parameters, self.DATASTORE, context)
        file_str = self.parameterAsString(parameters, self.FILES, context)
        files = file_str.split(";")

        srs_object = self.parameterAsCrs(parameters, self.SRS, context)
        srs = srs_object.authid()

        tag_data = self.parameterAsMatrix(parameters, self.TAGS, context)
        tags = tags_from_qgs_parameter_matrix_string(tag_data)

        try:
            manager = UploadRequestManager()

            # Create upload
            upload = manager.create_upload(
                datastore_id=datastore, name=name, description=description, srs=srs
            )

            # Add tags
            if len(tags) != 0:
                manager.add_tags(
                    datastore_id=datastore, upload_id=upload._id, tags=tags
                )

            # Add files
            for filename in files:
                manager.add_file(
                    datastore_id=datastore, upload_id=upload._id, filename=filename
                )

            # Close upload
            manager.close_upload(datastore_id=datastore, upload_id=upload._id)

            # Get create upload id
            upload_id = upload._id

            # Update feedback if upload attribute present
            if hasattr(feedback, "created_upload_id"):
                feedback.created_upload_id = upload_id

            # Wait for upload close after check
            self._wait_upload_close(datastore, upload_id)

        except UploadCreationException as exc:
            raise QgsProcessingException(f"Upload creation failed : {exc}")
        except FileUploadException as exc:
            raise QgsProcessingException(f"File upload failed : {exc}")
        except UploadClosingException as exc:
            raise QgsProcessingException(f"Upload closing failed : {exc}")

        return {self.CREATED_UPLOAD_ID: upload_id}

    def _wait_upload_close(self, datastore: str, upload_id: str) -> None:
        """
        Wait until upload is CLOSED or throw exception if status is UNSTABLE

        Args:
            datastore : (str) datastore id
            upload_id:  (str) upload id
        """
        try:
            manager = UploadRequestManager()
            upload = manager.get_upload(datastore_id=datastore, upload_id=upload_id)
            status = UploadStatus(upload.status)
            while status != UploadStatus.CLOSED and status != UploadStatus.UNSTABLE:
                upload = manager.get_upload(datastore_id=datastore, upload_id=upload_id)
                status = UploadStatus(upload.status)
                sleep(PlgOptionsManager.get_plg_settings().status_check_sleep)

            if status == UploadStatus.UNSTABLE:
                raise QgsProcessingException(
                    self.tr(
                        "Upload check failed. Check report in dashboard for more details."
                    )
                )

        except UnavailableUploadException as exc:
            raise QgsProcessingException(
                self.tr("Upload read failed : {0}").format(exc)
            )
