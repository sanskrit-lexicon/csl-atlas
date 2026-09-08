"""Proves the autouse offline guard in conftest is live: any socket attempt
inside this suite raises instead of reaching the network (H4352)."""

import socket
import urllib.request

import pytest

from conftest import NetworkDisabled


def test_socket_creation_is_blocked():
    with pytest.raises(NetworkDisabled):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def test_urllib_cannot_reach_out():
    with pytest.raises(Exception) as excinfo:
        urllib.request.urlopen("http://127.0.0.1:9/", timeout=1)
    assert "network is disabled" in str(excinfo.value) or isinstance(excinfo.value, NetworkDisabled)
