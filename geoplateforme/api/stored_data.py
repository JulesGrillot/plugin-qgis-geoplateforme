import json
import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Self

from qgis.core import (
    QgsBlockingNetworkRequest,
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# plugin
from geoplateforme.api.custom_exceptions import (
    AddTagException,
    DeleteStoredDataException,
    DeleteTagException,
    ReadStoredDataException,
)
from geoplateforme.toolbelt import NetworkRequestsManager, PlgLogger, PlgOptionsManager


class StorageType(Enum):
    UNDEFINED = "UNDEFINED"
    FILESYSTEM = "FILESYSTEM"
    POSTGRESQL = "POSTGRESQL"
    POSTGRESQL_DYN = "POSTGRESQL-DYN"
    S3 = "S3"


class StoredDataStep(Enum):
    UNDEFINED = "UNDEFINED"

    # Steps for VECTOR-DB type
    DATABASE_INTEGRATION = "DATABASE_INTEGRATION"
    TILE_GENERATION = "TILE_GENERATION"
    TILE_CREATED = "TILE_CREATED"

    # Steps for ROK4-PYRAMID-VECTOR type
    TILE_SAMPLE = "TILE_SAMPLE"
    TILE_PUBLICATION = "TILE_PUBLICATION"
    TILE_UPDATE = "TILE_UPDATE"
    PUBLISHED = "PUBLISHED"


class StoredDataStatus(Enum):
    CREATED = "CREATED"
    GENERATING = "GENERATING"
    GENERATED = "GENERATED"
    UNSTABLE = "UNSTABLE"
    MODIFYING = "MODIFYING"
    DELETED = "DELETED"


class StoredDataFeild(Enum):
    NAME = "name"
    DESCRIPTION = "description"
    TYPE = "type"
    VISIBILITY = "visibility"
    STATUS = "status"
    SRS = "srs"
    CONTACT = "contact"
    EDITION = "edition"
    SIZE = "size"
    LASTEVENT = "last_event"
    TAGS = "tags"
    BBOX = "bbox"


class StoredDataType(Enum):
    UNDEFINED = "UNDEFINED"
    VECTORDB = "VECTOR-DB"
    PYRAMIDVECTOR = "ROK4-PYRAMID-VECTOR"
    PYRAMIDRASTER = "ROK4-PYRAMID-RASTER"
    ARCHIVE = "ARCHIVE"
    GRAPHDB = "GRAPH-DB"
    GRAPHOSRM = "GRAPH-OSRM"
    GRAPHVALHALLA = "GRAPH-VALHALLA"
    INDEX = "INDEX"
    PYRAMID3DCOPC = "PYRAMID-3D-COPC"
    PYRAMID3DEPT = "PYRAMID-3D-EPT"


class StoredDataVisibility(Enum):
    PRIVATE = "PRIVATE"
    REFERENCED = "REFERENCED"
    PUBLIC = "PUBLIC"


@dataclass
class TableRelation:
    name: str
    attributes: {}
    primary_key: str


@dataclass
class StoredData:
    id: str
    datastore_id: str
    is_detailed: bool = False
    # Optional
    _name: Optional[str] = None
    _type: Optional[StoredDataType] = None
    _status: Optional[StoredDataStatus] = None
    _visibility: Optional[StoredDataVisibility] = None
    _description: Optional[str] = None
    _edition: Optional[dict] = None
    _contact: Optional[str] = None
    _tags: Optional[dict] = None
    _type_infos: Optional[dict] = None
    _extra: Optional[dict] = None
    _size: Optional[int] = None
    _srs: Optional[str] = None
    _extent: Optional[dict] = None
    _storage: Optional[dict] = None
    _last_event: Optional[dict] = None

    @property
    def name(self) -> str:
        """Returns the name of the stored data.

        :return: stored data name
        :rtype: str
        """
        if not self._name and not self.is_detailed:
            self.update_from_api()
        return self._name

    @property
    def type(self) -> StoredDataType:
        """Returns the type of the stored data.

        :return: stored data type
        :rtype: StoredDataType
        """
        if not self._type and not self.is_detailed:
            self.update_from_api()
        return self._type

    @property
    def status(self) -> StoredDataStatus:
        """Returns the status of the stored data.

        :return: stored data status
        :rtype: StoredDataStatus
        """
        if not self._status and not self.is_detailed:
            self.update_from_api()
        return self._status

    @property
    def visibility(self) -> StoredDataVisibility:
        """Returns the visibility of the stored data.

        :return: stored data visibility
        :rtype: StoredDataVisibility
        """
        if not self._visibility and not self.is_detailed:
            self.update_from_api()
        return self._visibility

    @property
    def description(self) -> str:
        """Returns the description of the stored data.

        :return: stored data description
        :rtype: str
        """
        if not self._description and not self.is_detailed:
            self.update_from_api()
        return self._description

    @property
    def edition(self) -> dict:
        """Returns the edition of the stored data.

        :return: stored data edition
        :rtype: dict
        """
        if not self._edition and not self.is_detailed:
            self.update_from_api()
        return self._edition

    @property
    def contact(self) -> str:
        """Returns the contact of the stored data.

        :return: stored data contact
        :rtype: str
        """
        if not self._contact and not self.is_detailed:
            self.update_from_api()
        return self._contact

    @property
    def tags(self) -> dict:
        """Returns the tags of the stored data.

        :return: stored data tags
        :rtype: dict
        """
        if not self._tags and not self.is_detailed:
            self.update_from_api()
        return self._tags

    @property
    def type_infos(self) -> dict:
        """Returns the type_infos of the stored data.

        :return: stored data type_infos
        :rtype: dict
        """
        if not self._type_infos and not self.is_detailed:
            self.update_from_api()
        return self._type_infos

    @property
    def extra(self) -> dict:
        """Returns the extra of the stored data.

        :return: stored data extra
        :rtype: dict
        """
        if not self._extra and not self.is_detailed:
            self.update_from_api()
        return self._extra

    @property
    def size(self) -> int:
        """Returns the size of the stored data.

        :return: stored data size
        :rtype: int
        """
        if not self._size and not self.is_detailed:
            self.update_from_api()
        return self._size

    @property
    def srs(self) -> str:
        """Returns the srs of the stored data.

        :return: stored data srs
        :rtype: str
        """
        if not self._srs and not self.is_detailed:
            self.update_from_api()
        return self._srs

    @property
    def extent(self) -> dict:
        """Returns the extent of the stored data.

        :return: stored data extent
        :rtype: dict
        """
        if not self._extent and not self.is_detailed:
            self.update_from_api()
        return self._extent

    @property
    def storage(self) -> dict:
        """Returns the storage of the stored data.

        :return: stored data storage
        :rtype: dict
        """
        if not self._storage and not self.is_detailed:
            self.update_from_api()
        return self._storage

    @property
    def last_event(self) -> dict:
        """Returns the last_event of the stored data.

        :return: stored data last_event
        :rtype: dict
        """
        if not self._last_event and not self.is_detailed:
            self.update_from_api()
        return self._last_event

    def update_from_api(self):
        manager = StoredDataRequestManager()
        data = manager.get_stored_data_json(self.datastore_id, self.id)

        if "name" in data:
            self._name = data["name"]
        if "type" in data:
            self._type = StoredDataType(data["type"])
        if "status" in data:
            self._status = StoredDataStatus(data["status"])
        if "visibility" in data:
            self._visibility = StoredDataVisibility(data["visibility"])
        if "description" in data:
            self._description = data["description"]
        if "edition" in data:
            self._edition = data["edition"]
        if "contact" in data:
            self._contact = data["contact"]
        if "extra" in data:
            self._extra = data["extra"]
        if "tags" in data:
            self._tags = data["tags"]
        if "type_infos" in data:
            self._type_infos = data["type_infos"]
        if "size" in data:
            self._size = data["size"]
        if "srs" in data:
            self._srs = data["srs"]
        if "storage" in data:
            self._storage = data["storage"]
        if "last_event" in data:
            self._last_event = data["last_event"]
        if "extent" in data:
            self._extent = data["extent"]
        self.is_detailed = True

    def get_last_event_date(self) -> str:
        result = ""
        if not self.last_event and not self.is_detailed:
            self.update_from_api()
        if self.last_event and "date" in self.last_event:
            result = self.last_event["date"]
        return result

    def get_storage_type(self) -> StorageType:
        result = StorageType.UNDEFINED
        if not self.is_detailed:
            self.update_from_api()
        if self.storage and "type" in self.storage:
            result = StorageType[self.storage["type"]]
        return result

    def get_tables(self) -> List[TableRelation]:
        tables = []
        if not self.is_detailed:
            self.update_from_api()
        if self.type_infos and "relations" in self.type_infos:
            tables = [
                TableRelation(
                    relation["name"], relation["attributes"], relation["primary_key"]
                )
                for relation in self.type_infos["relations"]
                if relation["type"] == "TABLE"
            ]
        return tables

    def zoom_levels(self) -> List:
        zoom_levels = []
        if not self.is_detailed:
            self.update_from_api()
        if self.type_infos and "levels" in self.type_infos:
            zoom_levels = self.type_infos["levels"]
        return zoom_levels

    def get_current_step(self) -> StoredDataStep:
        """
        Define current stored data step from available tags.

        Returns: StoredDataStep

        """
        if self.type == StoredDataType.VECTORDB:
            result = self._get_vector_db_step()
        elif self.type == StoredDataType.PYRAMIDVECTOR:
            result = self._get_pyramid_step()
        else:
            result = StoredDataStep.UNDEFINED
        return result

    def _get_vector_db_step(self) -> StoredDataStep:
        """
        Define current stored data step for vector-db from available tags.

        Returns: StoredDataStep

        """
        if not self.tags and not self.is_detailed:
            self.update_from_api()
        if self.tags:
            if "upload_id" in self.tags and "proc_int_id" in self.tags:
                if "pyramid_id" in self.tags:
                    result = StoredDataStep.TILE_CREATED
                else:
                    result = StoredDataStep.TILE_GENERATION
            else:
                result = StoredDataStep.DATABASE_INTEGRATION
        else:
            result = StoredDataStep.DATABASE_INTEGRATION
        return result

    def _get_pyramid_step(self) -> StoredDataStep:
        """
        Define current stored data step for pyramid from available tags.

        Returns: StoredDataStep

        """
        result = StoredDataStep.UNDEFINED
        if not self.tags and not self.is_detailed:
            self.update_from_api()
        if self.tags:
            if (
                "upload_id" in self.tags
                and "proc_int_id" in self.tags
                and "vectordb_id" in self.tags
                and "proc_pyr_creat_id" in self.tags
            ):
                result = StoredDataStep.TILE_PUBLICATION
                if "is_sample" in self.tags:
                    result = StoredDataStep.TILE_SAMPLE
                elif "initial_pyramid_id" in self.tags:
                    result = StoredDataStep.TILE_UPDATE
                # "published tag" should be defined if a tile is published
                # cf : https://github.com/IGNF/geoplateforme-site/blob/master/docs/developer/workflow.md#3-publier
                # But it seems that the tag is not added
                # an issue was created : https://github.com/IGNF/geoplateforme-site/issues/94
                # If pyramid is not in TILE_SAMPLE or TILE_UPDATE steps it means that it's published if tms_url available
                elif "published" in self.tags or "tms_url" in self.tags:
                    result = StoredDataStep.PUBLISHED
        return result

    def create_extent_layer(self) -> QgsVectorLayer:
        """
        Create extent layer from geojson contains in extent key

        Returns: QgsVectorLayer (invalid layer if extent not defined)

        """
        if not self.is_detailed:
            self.update_from_api()
        layer = QgsVectorLayer(json.dumps(self.extent), f"{self.name}-extent", "ogr")
        layer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        return layer

    @classmethod
    def from_dict(cls, datastore_id: str, val: dict) -> Self:
        """Load object from a dict.

        Args
            datastore_id: (str) datastore id
            val (dict): dict value to load

        Return
            Self: object with attributes filled from dict.
        """
        res = cls(
            id=val["_id"],
            datastore_id=datastore_id,
        )

        if "name" in val:
            res._name = val["name"]
        if "type" in val:
            res._type = StoredDataType(val["type"])
        if "status" in val:
            res._status = StoredDataStatus(val["status"])
        if "visibility" in val:
            res._visibility = StoredDataVisibility(val["visibility"])
        if "description" in val:
            res._description = val["description"]
        if "edition" in val:
            res._edition = val["edition"]
        if "contact" in val:
            res._contact = val["contact"]
        if "extra" in val:
            res._extra = val["extra"]
        if "tags" in val:
            res._tags = val["tags"]
        if "type_infos" in val:
            res._type_infos = val["type_infos"]
        if "size" in val:
            res._size = val["size"]
        if "srs" in val:
            res._srs = val["srs"]
        if "storage" in val:
            res.s_torage = val["storage"]
        if "last_event" in val:
            res._last_event = val["last_event"]
        if "extent" in val:
            res._extent = val["extent"]

        return res


class StoredDataRequestManager:
    MAX_LIMIT = 50

    def get_base_url(self, datastore_id: str) -> str:
        """
        Get base url for stored data for a datastore

        Args:
            datastore_id: (str) datastore id

        Returns: url for uploads

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore_id}/stored_data"

    def __init__(self):
        """
        Helper for stored_data request

        """
        self.log = PlgLogger().log
        self.request_manager = NetworkRequestsManager()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_stored_data_list(
        self,
        datastore: str,
        with_fields: Optional[List[StoredDataFeild]] = None,
        tags: Optional[dict] = None,
    ) -> List[StoredData]:
        """
        Get list of stored data

        Args:
            datastore: (str) datastore id
            with_fields: (Optional[List[StoredDataFeild]]) list of field to be add to the response
            tags: (Optional[dict]) list of tags to filter data

        Returns: list of available stored data, raise ReadStoredDataException otherwise
        """
        self.log(f"{__name__}.get_stored_data_list(datastore:{datastore})")

        nb_value = self._get_nb_available_stored_data(datastore, tags)
        nb_request = math.ceil(nb_value / self.MAX_LIMIT)
        result = []
        for page in range(0, nb_request):
            result += self._get_stored_data_list(
                datastore, page + 1, self.MAX_LIMIT, with_fields, tags
            )
        return result

    def _get_stored_data_list(
        self,
        datastore_id: str,
        page: int = 1,
        limit: int = MAX_LIMIT,
        with_fields: Optional[List[StoredDataFeild]] = None,
        tags: Optional[dict] = None,
    ) -> List[StoredData]:
        """
        Get list of stored data

        Args:
            datastore_id: (str) datastore id
            page: (int) page number (start at 1)
            limit: (int)
            with_fields: (List[StoredDataFeild]) list of field to be add to the response
            tags: (dict) list of tags to filter data

        Returns: list of available stored data, raise ReadStoredDataException otherwise
        """
        # request additionnal fields
        add_fields = ""
        if with_fields:
            for field in with_fields:
                add_fields += f"&fields={field.value}"
        # Add filter on tags
        tags_url = ""
        if tags:
            for key, value in dict.items(tags):
                tags_url += f"&tags[{key}]={value}"

        reply = self.request_manager.get_url(
            url=QUrl(
                f"{self.get_base_url(datastore_id)}?page={page}&limit={limit}{add_fields}{tags_url}"
            ),
            config_id=self.plg_settings.qgis_auth_id,
        )
        data = json.loads(reply.data())

        return [StoredData.from_dict(datastore_id, stored_data) for stored_data in data]

    def _get_nb_available_stored_data(
        self, datastore_id: str, tags: Optional[dict] = None
    ) -> int:
        """
        Get number of available stored data

        Args:
            datastore_id: (str) datastore id
            tags: (dict) list of tags to filter data

        Returns: (int) number of available data, raise ReadStoredDataException in case of request error

        """
        # For now read with maximum limit possible
        tags_url = ""
        if tags:
            for key, value in dict.items(tags):
                tags_url += f"&tags[{key}]={value}"
        req_reply = self.request_manager.get_url(
            url=QUrl(f"{self.get_base_url(datastore_id)}?limit=1{tags_url}"),
            config_id=self.plg_settings.qgis_auth_id,
            return_req_reply=True,
        )

        # check response
        content_range = req_reply.rawHeader(b"Content-Range").data().decode("utf-8")
        match = re.match(
            r"(?P<min>\d+)\s?-\s?(?P<max>\d+)?\s?\/?\s?(?P<nb_val>\d+|\*)?",
            content_range,
        )
        if match:
            nb_val = int(match.group("nb_val"))
        else:
            raise ReadStoredDataException(
                f"Invalid Content-Range {content_range} not min-max/nb_val as expected"
            )
        return nb_val

    def get_stored_data(self, datastore_id: str, stored_data_id: str) -> StoredData:
        """
        Get stored data by id

        Args:
            datastore_id: (str) datastore id
            stored_data_id: (str) stored data id

        Returns: stored data, raise ReadStoredDataException otherwise
        """
        self.log(
            f"{__name__}.get_stored_data(datastore:{datastore_id},stored_data:{stored_data_id})"
        )
        return StoredData.from_dict(
            datastore_id, self.get_stored_data_json(datastore_id, stored_data_id)
        )

    def get_stored_data_json(self, datastore_id: str, stored_data_id: str) -> dict:
        """
        Get dict values of stored data

        Args:
            datastore_id: (str) datastore id
            stored_data_id: (str) stored data id

        Returns: dict values of stored data, raise ReadStoredDataException otherwise
        """
        reply = self.request_manager.get_url(
            url=QUrl(f"{self.get_base_url(datastore_id)}/{stored_data_id}"),
            config_id=self.plg_settings.qgis_auth_id,
        )
        return json.loads(reply.data())

    def delete(self, datastore_id: str, stored_data_id: str) -> None:
        """
        Delete a stored data. Raise DeleteStoredDataException if an error occurs

        Args:
            datastore_id: (str) datastore id
            stored_data_id: (str) stored data id
        """
        self.log(
            f"{__name__}.delete(datastore:{datastore_id},stored_data:{stored_data_id})"
        )

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_delete = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore_id)}/{stored_data_id}")
        )
        # send request
        resp = self.ntwk_requester_blk.deleteResource(req_delete)

        # check response
        if resp != QgsBlockingNetworkRequest.ErrorCode.NoError:
            req_reply = self.ntwk_requester_blk.reply()
            data = json.loads(req_reply.content().data().decode("utf-8"))
            raise DeleteStoredDataException(
                f"Error while deleting stored_data : {self.ntwk_requester_blk.errorMessage()}. Reply error: {data}"
            )

    def add_tags(self, datastore_id: str, stored_data_id: str, tags: dict) -> None:
        """
        Add tags to stored data

        Args:
            datastore_id:  (str) datastore id
            stored_data_id: (str) stored_data id
            tags: (dict) dictionary of tags
        """
        self.log(
            f"{__name__}.add_tags(datastore:{datastore_id},stored_data:{stored_data_id}, tags:{tags})"
        )

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore_id)}/{stored_data_id}/tags")
        )

        # headers
        req_post.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json"
        )

        # encode data
        data = QByteArray()
        data.append(json.dumps(tags))

        # send request
        resp = self.ntwk_requester_blk.post(req_post, data=data, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.ErrorCode.NoError:
            raise AddTagException(
                f"Error while adding tag to stored_data : {self.ntwk_requester_blk.errorMessage()}"
            )

    def delete_tags(self, datastore_id: str, stored_data_id: str, tags: list) -> None:
        """
        Delete tags of stored data

        Args:
            datastore_id:  (str) datastore id
            stored_data_id: (str) stored_data id
            tags: (list) list of tags
        """
        self.log(
            f"{__name__}.delete_tags(datastore:{datastore_id},stored_data:{stored_data_id}, tags:{tags})"
        )

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        url = f"{self.get_base_url(datastore_id)}/{stored_data_id}/tags?"
        # Add all tag to remove
        for tag in tags:
            url += f"&tags={tag}"

        req_del = QNetworkRequest(QUrl(url))

        # headers
        req_del.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json"
        )

        # send request
        resp = self.ntwk_requester_blk.deleteResource(req_del)

        # check response
        if resp != QgsBlockingNetworkRequest.ErrorCode.NoError:
            req_reply = self.ntwk_requester_blk.reply()
            data = json.loads(req_reply.content().data().decode("utf-8"))
            raise DeleteTagException(
                f"Error while deleting tags for stored data : {self.ntwk_requester_blk.errorMessage()}. Reply error: {data}"
            )
