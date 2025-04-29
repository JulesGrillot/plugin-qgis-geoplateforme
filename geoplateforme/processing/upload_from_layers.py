# standard
from typing import Any, Dict, List, Optional

# PyQGIS
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterMatrix,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

from geoplateforme.processing.upload_from_files import GpfUploadFromFileAlgorithm

# plugin
from geoplateforme.processing.utils import (
    get_shapefile_associated_files,
    get_short_string,
    get_user_manual_url,
)


class GpfUploadFromLayersAlgorithm(QgsProcessingAlgorithm):
    DATASTORE = "DATASTORE"
    NAME = "NAME"
    DESCRIPTION = "DESCRIPTION"
    LAYERS = "LAYERS"
    TAGS = "TAGS"

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
        return GpfUploadFromLayersAlgorithm()

    def name(self):
        return "upload_from_layer"

    def displayName(self):
        return self.tr("Création livraison depuis des couches vectorielles")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return get_user_manual_url(self.name())

    def shortHelpString(self):
        return get_short_string(self.name(), self.displayName())

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                name=self.DATASTORE,
                description=self.tr("Identifiant de l'entrepôt"),
            )
        )

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                name=self.LAYERS,
                description=self.tr("Couches vectorielles à livrer"),
                layerType=Qgis.ProcessingSourceType.VectorAnyGeometry,
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
            QgsProcessingParameterMatrix(
                name=self.TAGS,
                description=self.tr("Tags"),
                headers=[self.tr("Tag"), self.tr("Valeur")],
            )
        )

    def processAlgorithm(
        self,
        parameters: Dict[str, Any],
        context: QgsProcessingContext,
        feedback: Optional[QgsProcessingFeedback],
    ) -> Dict[str, Any]:
        """Runs the algorithm using the specified parameters.

        :param parameters: algorithm parameters
        :type parameters: Dict[str, Any]
        :param context: processing context
        :type context: QgsProcessingContext
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :raises QgsProcessingException: Multiple crs for input layers
        :raises QgsProcessingException: Error in upload creation
        :return: algorithm results
        :rtype: Dict[str, Any]
        """
        name = self.parameterAsString(parameters, self.NAME, context)
        description = self.parameterAsString(parameters, self.DESCRIPTION, context)
        datastore = self.parameterAsString(parameters, self.DATASTORE, context)
        tags = self.parameterAsMatrix(parameters, self.TAGS, context)

        layers = self.parameterAsLayerList(parameters, self.LAYERS, context)

        # define CRS from input layers
        srs: Optional[QgsCoordinateReferenceSystem] = None

        for layer in layers:
            layer_crs = layer.dataProvider().crs()
            if not srs:
                srs = layer_crs
            elif layer_crs != srs:
                raise QgsProcessingException(
                    self.tr(
                        "Toutes les couches doivent avoir le même système de coordonnées pour la livraison."
                    )
                )

        # define files from input layers
        files: List[str] = []
        for layer in layers:
            if layer.storageType() == "GPKG":
                source = layer.source()
                path = source.split("|")[0]
                files.append(path)
            elif layer.storageType() == "ESRI Shapefile":
                source = layer.source()
                files.extend(get_shapefile_associated_files(source))

        algo_str = f"geoplateforme:{GpfUploadFromFileAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        params = {
            GpfUploadFromFileAlgorithm.DATASTORE: datastore,
            GpfUploadFromFileAlgorithm.NAME: name,
            GpfUploadFromFileAlgorithm.DESCRIPTION: description,
            GpfUploadFromFileAlgorithm.SRS: srs,
            GpfUploadFromFileAlgorithm.FILES: ";".join(files),
            GpfUploadFromFileAlgorithm.TAGS: tags,
        }

        results, successful = alg.run(params, context, feedback)
        if successful:
            created_upload_id = results[GpfUploadFromFileAlgorithm.CREATED_UPLOAD_ID]
        else:
            raise QgsProcessingException(self.tr("Upload creation failed"))

        return {self.CREATED_UPLOAD_ID: created_upload_id}
