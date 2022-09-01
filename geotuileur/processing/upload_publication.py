# standard
import json

# PyQGIS
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

from geotuileur.api.configuration import Configuration, ConfigurationRequestManager

# Plugin
from geotuileur.api.custom_exceptions import (
    ConfigurationCreationException,
    OfferingCreationException,
    UnavailableEndpointException,
)
from geotuileur.api.datastore import DatastoreRequestManager
from geotuileur.api.stored_data import StoredDataRequestManager
from geotuileur.toolbelt import PlgLogger

data_type = "WMTS-TMS"


class UploadPublicationAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    STORED_DATA = "stored_data"
    NAME = "name"
    TITLE = "title"
    ABSTRACT = "abstract"
    PUBLICATION_URL = "publication_url"
    KEYWORDS = "keywords"
    LAYER_NAME = "layer_name"
    METADATA = "metadata"
    BOTTOM_LEVEL = "bottom_level"
    TOP_LEVEL = "top_level"
    URL_TITLE = "title"
    URL_ATTRIBUTION = "url_attribution"
    VISIBILITY = "visibility"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

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

            datastore = data[self.DATASTORE]
            stored_data_id = data.get(self.STORED_DATA)

            layer_name = data.get(self.LAYER_NAME)
            abstract = data.get(self.ABSTRACT)
            bottom_level = data.get(self.BOTTOM_LEVEL)
            top_level = data.get(self.TOP_LEVEL)
            metadata = data.get(self.METADATA)
            name = data.get(self.NAME)
            publication_visibility = data.get(self.VISIBILITY, "PUBLIC")
            title = data.get(self.TITLE)
            url = data.get(self.URL_ATTRIBUTION)
            url_title = data.get(self.URL_TITLE)

            # create (post) configuration from input data
            try:
                manager_configuration = ConfigurationRequestManager()

                configuration = Configuration(
                    type_data="WMTS-TMS",
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

            except ConfigurationCreationException as exc:
                raise QgsProcessingException(f"exc configuration id : {exc}")

            # get the endpoint for the publication
            try:
                manager_endpoint = DatastoreRequestManager()
                res = manager_endpoint.get_endpoint(
                    datastore=datastore, data_type=data_type
                )

                publication_endpoint = res
            except UnavailableEndpointException as exc:
                raise QgsProcessingException(f"exc endpoint : {exc}")

            # create publication (offering)
            try:

                manager_offering = ConfigurationRequestManager()
                res = manager_offering.create_offering(
                    visibility=publication_visibility,
                    endpoint=publication_endpoint,
                    datastore=datastore,
                    configuration_id=configuration_id,
                )
                publication_urls = res
            except OfferingCreationException as exc:
                raise QgsProcessingException(f"exc publication url : {exc}")

            # One url defined
            publication_url = publication_urls[0]
            # Remove tms| indication
            url_data = publication_url[len("tms|") : len(publication_url)]

            try:
                # Update stored data tags
                manager = StoredDataRequestManager()
                manager.add_tags(
                    datastore=datastore,
                    stored_data=stored_data_id,
                    tags={"tms_url": url_data, "published": "true"},
                )
            except StoredDataRequestManager.AddTagException as exc:
                raise QgsProcessingException(f"exc tag update url : {exc}")

            return {
                self.PUBLICATION_URL: url_data,
            }
