import logging

from qgis.core import QgsBlockingNetworkRequest, QgsNetworkReplyContent
from qgis.PyQt.QtCore import QDateTime, Qt
from qgis.PyQt.QtNetwork import QNetworkRequest

logger = logging.getLogger(__name__)


def send_qgs_blocking_request(
    ntwk_requester_blk: QgsBlockingNetworkRequest,
    req: QNetworkRequest,
    exception_type: type,
    expected_type: str = "application/json; charset=utf-8",
) -> QgsNetworkReplyContent:
    # headers
    req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

    # send request
    resp = ntwk_requester_blk.get(req, forceRefresh=True)

    # check response
    if resp != QgsBlockingNetworkRequest.NoError:
        raise exception_type(ntwk_requester_blk.errorMessage())

    # check response
    req_reply = ntwk_requester_blk.reply()
    content_type = req_reply.rawHeader(b"Content-Type")
    if not content_type == expected_type:
        raise exception_type(
            f"Response mime-type is '{content_type}' not '{expected_type}' as required."
        )
    return req_reply


def as_localized_datetime(date: str) -> str:
    """Try to convert raw creation date as localized datetime using Qt.

    :return: localized date time (or raw creation string if conversion fails)
    :rtype: str
    """
    try:
        dt = QDateTime.fromString(date, Qt.ISODate)
        return dt.toString(Qt.DefaultLocaleLongDate)
    except Exception as exc:
        logger.error(f"Datetime parseing failded. Trace: {exc}")
        return date
