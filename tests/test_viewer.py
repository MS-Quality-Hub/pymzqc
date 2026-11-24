"""Browser tests for the static mzQC viewer (mzqcaccessories/viewer).

They need Playwright and a Chromium build (``pip install pymzqc[dev]`` and
``playwright install chromium``) and are skipped otherwise.
"""
import functools
import http.server
import os
import threading
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parent.parent
VIEWER = "mzqcaccessories/viewer"


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def base_url():
    handler = functools.partial(_QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _cached_chromium():
    """Fallback: any Chromium Playwright cached earlier (other Playwright versions)."""
    cache = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", Path.home() / ".cache" / "ms-playwright"))
    patterns = ["chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
                "chromium-*/chrome-linux64/chrome"]
    for pattern in patterns:
        for exe in sorted(cache.glob(pattern), reverse=True):
            yield str(exe)


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except sync_api.Error:
            b = None
            for exe in _cached_chromium():
                try:
                    b = p.chromium.launch(executable_path=exe)
                    break
                except sync_api.Error:
                    continue
            if b is None:
                pytest.skip("no Chromium available for Playwright (run: playwright install chromium)")
        yield b
        b.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1400, "height": 900})
    pg = context.new_page()
    errors = []
    pg.on("pageerror", lambda exc: errors.append(str(exc)))
    yield pg
    context.close()
    assert not errors, f"JavaScript errors: {errors}"


def test_core_unit_tests(page, base_url):
    page.goto(f"{base_url}/{VIEWER}/tests/index.html")
    results = page.evaluate("window.__testResults")
    failed = [r for r in results if not r["ok"]]
    assert results and not failed, failed
