"""Tests for the online validator app (pymzqc[onlinevalidator])."""
import subprocess
import sys

import pytest

MODULE = "mzqcaccessories.onlinevalidator.mzqc_online_validator"


def test_missing_extra_names_the_install_command():
    # Block flask imports in a fresh interpreter to simulate a base install.
    code = (
        "import sys; sys.modules['flask'] = None\n"
        f"import {MODULE}\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "pip install pymzqc[onlinevalidator]" in proc.stderr


@pytest.fixture
def client():
    pytest.importorskip("flask")
    pytest.importorskip("flask_restful")
    pytest.importorskip("flask_cors")
    from mzqcaccessories.onlinevalidator.mzqc_online_validator import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_status(client):
    assert client.get("/status/").get_json()["status"] == "API is running"


def test_viewer_is_served(client):
    resp = client.get("/viewer/")
    assert resp.status_code == 200
    assert b"<title>mzQC Viewer</title>" in resp.data
    for asset in ("mzqc-core.js", "mzqc-plot.js", "mzqc-viewer.js", "mzqc-viewer.css"):
        assert client.get(f"/viewer/{asset}").status_code == 200, asset
    assert client.get("/viewer").status_code in (301, 302, 308)
    assert client.get("/viewer/../validator_core.py").status_code == 404
