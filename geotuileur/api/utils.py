from qgis.core import QgsBlockingNetworkRequest, QgsNetworkReplyContent
from qgis.PyQt.QtNetwork import QNetworkRequest


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
