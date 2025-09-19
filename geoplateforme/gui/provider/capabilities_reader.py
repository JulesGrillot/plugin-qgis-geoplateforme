import logging
from typing import Optional
from xml.dom.minidom import parseString

from qgis.PyQt.QtCore import QUrl

from geoplateforme.toolbelt import NetworkRequestsManager, PlgLogger

logger = logging.getLogger(__name__)


def getFirstElementByTagName(parent, name):
    try:
        return parent.getElementsByTagName(name)[0]
    except Exception:
        return None


def getFirstElementValueByTagName(parent, name):
    try:
        return parent.getElementsByTagName(name)[0].firstChild.nodeValue
    except Exception:
        return ""


def read_wmts_layer_capabilities(
    url: str, layerName: str, authid: Optional[str] = None
) -> Optional[dict]:
    """Get layer informations from GetCapabilities

    :param url: service url
    :type url: str
    :param layerName: layer name
    :type layerName: str
    :return: a dict containing format, style and tilematrixset if layer exist, else None
    :rtype: dict
    """
    request_manager = NetworkRequestsManager()
    log = PlgLogger().log

    try:
        reply = request_manager.get_url(
            url=QUrl(f"{url}?service=WMTS&request=GetCapabilities"), config_id=authid
        )
    except ConnectionError as err:
        log(
            f"Unable to download Capabilities : {err}",
            log_level=2,
            push=True,
        )
        return None

    try:
        capabilities = parseString(reply.data())
    except Exception as err:
        log(
            f"Unable to parse Capabilities : {err}",
            log_level=2,
            push=True,
        )
        return None

    contents = getFirstElementByTagName(capabilities, "Contents")

    # Search for layer
    targetLayer = None
    for layer in contents.getElementsByTagName("Layer"):
        identifier = getFirstElementValueByTagName(layer, "ows:Identifier")
        if identifier == layerName:
            targetLayer = layer
            break

    if not targetLayer:
        log(
            f"Could not find layer {layerName} in capabilities",
            log_level=2,
            push=True,
        )
        return None

    # Get first supported tile matrix
    tileMatrixSetLink = getFirstElementByTagName(targetLayer, "TileMatrixSetLink")
    tileMatrixName = getFirstElementValueByTagName(tileMatrixSetLink, "TileMatrixSet")

    if not tileMatrixName:
        log(
            f"Could not find tileMatrixSet for layer {layerName}",
            log_level=2,
            push=True,
        )
        return None

    # Determine style
    for style in targetLayer.getElementsByTagName("Style"):
        if style.getAttribute("isDefault") == "true":
            styleIdentifier = getFirstElementValueByTagName(style, "ows:Identifier")
            break

    # Format
    format = getFirstElementValueByTagName(targetLayer, "Format")

    return {
        "format": format,
        "tileMatrixSet": tileMatrixName,
        "style": styleIdentifier,
    }


def read_tms_layer_capabilities(url: str) -> Optional[dict]:
    """Get tms format from GetCapabilities

    :param url: service url
    :type url: str
    :return:  a dict containing format, zmin and zmax if exist, else None
    :rtype: dict
    """
    request_manager = NetworkRequestsManager()
    log = PlgLogger().log

    try:
        reply = request_manager.get_url(
            url=QUrl(f"{url}"),
        )
    except ConnectionError as err:
        log(
            f"Unable to download Capabilities : {err}",
            log_level=2,
            push=True,
        )
        return None

    try:
        capabilities = parseString(reply.data())
    except Exception as err:
        log(
            f"Unable to parse Capabilities : {err}",
            log_level=2,
            push=True,
        )
        return None

    tile_format = getFirstElementByTagName(capabilities, "TileFormat")
    if tile_format:
        format_ext = tile_format.getAttribute("extension")
    else:
        return None

    tile_srs = getFirstElementByTagName(capabilities, "SRS")
    if tile_srs:
        srs = tile_srs.firstChild.nodeValue
    else:
        return None

    zmin = None
    zmax = None
    for tile_set in capabilities.getElementsByTagName("TileSet"):
        href = tile_set.getAttribute("href")
        z = href.split("/")[-1]
        if zmin is None or z < zmin:
            zmin = z
        if zmax is None or z > zmax:
            zmax = z
    styles = []
    for metadata in capabilities.getElementsByTagName("Metadata"):
        type = metadata.getAttribute("type")
        mime = metadata.getAttribute("mime-type")
        if type == "Other" and mime == "application/json":
            styles.append(metadata.getAttribute("href"))

    return {
        "format": format_ext,
        "zmin": zmin,
        "zmax": zmax,
        "srs": srs,
        "styles": styles,
    }
