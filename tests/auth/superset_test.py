"""
Test username:password authentication mechanism.
"""

from pytest_mock import MockerFixture
from requests_mock.mocker import Mocker
from yarl import URL

from preset_cli.auth.superset import SupersetJWTAuth, UsernamePasswordAuth


def test_username_password_auth(requests_mock: Mocker) -> None:
    """
    Tests for the username/password authentication mechanism.
    """
    csrf_token = "CSFR_TOKEN"
    requests_mock.post(
        "https://superset.example.com/api/v1/security/login",
        json={"access_token": "myAccessToken"},
    )
    requests_mock.get(
        "https://superset.example.com/api/v1/security/csrf_token",
        json={"result": csrf_token},
    )

    auth = UsernamePasswordAuth(
        URL("https://superset.example.com/"),
        "admin",
        "password123",
    )

    assert (
        requests_mock.last_request.json()
        == {
            "username": "admin",
            "password": "password123",
            "provider": "db",
        }
    )

    assert auth.get_headers() == {
        "Authorization": "Bearer myAccessToken",
        "X-CSRFToken": csrf_token,
    }


def test_jwt_auth_superset(mocker: MockerFixture) -> None:
    """
    Test the ``JWTAuth`` authentication mechanism for Superset tenant.
    """
    auth = SupersetJWTAuth("my-token", URL("https://example.com/"))
    mocker.patch.object(auth, "get_csrf_token", return_value="myCSRFToken")

    assert auth.get_headers() == {
        "Authorization": "Bearer my-token",
        "X-CSRFToken": "myCSRFToken",
    }


def test_get_csrf_token(requests_mock: Mocker) -> None:
    """
    Test the get_csrf_token method.
    """
    auth = SupersetJWTAuth("my-token", URL("https://example.com/"))
    requests_mock.get(
        "https://example.com/api/v1/security/csrf_token",
        json={"result": "myCSRFToken"},
    )

    assert auth.get_csrf_token("my-token") == "myCSRFToken"
