import pytest_httpserver

from geoplateforme.processing.permissions.delete_permission import (
    DeletePermissionAlgorithm,
)
from tests.qgis.processings.conftest import run_alg


def test_key_delete(
    data_geopf_srv: pytest_httpserver.HTTPServer,
):
    """
    Check no error is raised when server return valid return code

    Args:
        data_geopf_srv: pytest fixture to simulate server and mock plugin settings
    """
    datastore_id = "datastore_id"
    permission_id = "permission_id"

    # Respond valid return code
    data_geopf_srv.expect_oneshot_request(
        f"/api/datastores/{datastore_id}/permissions/{permission_id}", method="DELETE"
    ).respond_with_data(status=202)

    params = {
        DeletePermissionAlgorithm.PERMISSION_ID: permission_id,
        DeletePermissionAlgorithm.DATASTORE_ID: datastore_id,
    }
    _, success = run_alg(DeletePermissionAlgorithm().name(), params)
    assert success
