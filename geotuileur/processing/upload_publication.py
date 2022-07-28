# standard
import json

# PyQGIS
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geotuileur.api.configuration import Configuration, ConfigurationRequestManager
from geotuileur.api.endpoint import EndpointRequestManager
from geotuileur.api.offering import OfferingRequestManager
from geotuileur.toolbelt import PlgLogger


class UploadPublicationAlgorithm(QgsProcessingAlgorithm):

    ABSTRACT = "abstract"
    BOTTOM_LEVEL = "bottom_level"
    CONFIGURATION_ID = "configuration_id"
    PUBLICATION_URL = "publication_url"
    DATASTORE = "datastore"
    ENDPOINT = "endpoint"
    INPUT_JSON = "INPUT_JSON"
    KEYWORDS = "keywords"
    LAYER_NAME = "layer_name"
    METADATA = "metadata"
    NAME = "name"
    STORED_DATA = "stored_data"
    TOP_LEVEL = "top_level"
    TITLE = "title"
    TYPE_DATA = "type_data"
    URL_ATTRIBUTION = "url_attribution"
    URL_TITLE = "title"
    VISIBILITY = "visibility"

    def tr(self, string):
        return QCoreApplication.translate(
            "Create an publication for IGN Geotuileur platform", string
        )

    def createInstance(self):
        return UploadPublicationAlgorithm()

    def name(self):
        return "upload_configuration "

    def displayName(self):
        return self.tr("Create configuration")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):

        return self.tr(
            "Publication in geotuileur platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.TYPE_DATA}": wanted  type data  (str),\n'
            f'    "{self.DATASTORE}": wanted  datastore  (str),\n'
            f'    "{self.METADATA}": wanted  metadata (str),\n'
            f'    "{self.NAME}": wanted datastore name (str),\n'
            f'    "{self.LAYER_NAME}":wanted  layer name (str),\n'
            f'    "{self.KEYWORDS}": wanted keywords (str),\n'
            f'    "{self.STORED_DATA}":wanted stored data name (str),\n'
            f'    "{self.BOTTOM_LEVEL}": bottom level (int), value between 1 and 21,\n'
            f'    "{self.TOP_LEVEL}": top level (int), value between 1 and 21,\n'
            f'    "{self.TITLE}": title (str) ,\n'
            f'    "{self.ABSTRACT}": little abstract (str) ,\n'
            f'    "{self.URL_TITLE}": url title  (str),\n'
            f'    "{self.URL_ATTRIBUTION}": url attribution (str) ,\n'
            f'    "{self.VISIBILITY}": Publication visibility  (str) ,\n'
            "}\n"
            f"Returns created configuration id in {self.PUBLICATION_URL} results"
        )

    def initAlgorithm(self, config=None):
        self.log = PlgLogger().log

        self.addParameter(
            QgsProcessingParameterString(
                name=self.INPUT_JSON,
                description=self.tr("Input .json file"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        filename = self.parameterAsFile(parameters, self.INPUT_JSON, context)
        self.log(message=f"Input publication configuration: {filename}", log_level=4)

        # load processing configuration from the JSON (--> created through qwp_status.py)
        with open(filename, "r") as file:
            data = json.load(file)

            abstract = data.get(self.ABSTRACT)
            bottom_level = data.get(self.BOTTOM_LEVEL)
            datastore = data[self.DATASTORE]
            layer_name = data.get(self.LAYER_NAME)
            metadata = data.get(self.METADATA)
            name = data.get(self.NAME)
            publication_endpoint = data.get(self.ENDPOINT)
            publication_visibility = data.get(self.VISIBILITY, "PUBLIC")
            stored_data_id = data.get(self.STORED_DATA)
            title = data.get(self.TITLE)
            top_level = data.get(self.TOP_LEVEL)
            type_data = data.get(self.TYPE_DATA)
            url = data.get(self.URL_ATTRIBUTION)
            url_title = data.get(self.URL_TITLE)
            configuration_id = data.get(self.CONFIGURATION_ID)

            # create (post) configuration from input data
            try:
                manager_configuration = ConfigurationRequestManager()

                configuration = Configuration(
                    type_data=type_data,
                    metadata=metadata,
                    name=name,
                    layer_name=layer_name,
                    type_infos={},
                    attribution={},
                )
                configuration.title = title
                configuration.abstract = abstract
                configuration.url_title = url_title
                configuration.url = url

                # response = configuration
                res = manager_configuration.create_configuration(
                    datastore=datastore,
                    stored_data=stored_data_id,
                    top_level=top_level,
                    bottom_level=bottom_level,
                    configuration=configuration,
                )

                self.log(message=f"res configuration: {res}", log_level=4)

                configuration_id = res

            except ConfigurationRequestManager.ConfigurationCreationException as exc:
                raise QgsProcessingException(f"exc configuration id : {exc}")

            # get the endpoint
            try:
                manager_endpoint = EndpointRequestManager()
                res = manager_endpoint.create_endpoint(
                    datastore=datastore,
                )

                publication_endpoint = res
            except EndpointRequestManager.EndpointCreationException as exc:
                raise QgsProcessingException(f"exc endpoint : {exc}")

            # create publication (offering)
            try:

                manager_offering = OfferingRequestManager()
                res = manager_offering.create_offering(
                    visibility=publication_visibility,
                    endpoint=publication_endpoint,
                    datastore=datastore,
                    configuration_id=configuration_id,
                )
                publication_url = res
            except OfferingRequestManager.OfferingCreationException as exc:
                raise QgsProcessingException(f"exc publication url : {exc}")

            return {
                self.PUBLICATION_URL: str(publication_url),
            }
