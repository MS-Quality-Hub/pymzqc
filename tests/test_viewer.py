"""Browser tests for the static mzQC viewer (mzqcaccessories/viewer).

They need Playwright and a Chromium build (``pip install pymzqc[dev]`` and
``playwright install chromium``) and are skipped otherwise.
"""
import functools
import glob
import http.server
import json
import os
import threading
from pathlib import Path
from urllib.parse import quote

import pytest

from mzqc.MZQCFile import JsonSerialisable as mzqc_io

sync_api = pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parent.parent
VIEWER = "mzqcaccessories/viewer"
SHOWCASE = f"{VIEWER}/tests/fixtures/showcase.mzQC"
# POSIX paths, so they match PYMZQC_NORMALISED and the server URLs on Windows too
EXAMPLES = sorted(Path(p).relative_to(ROOT).as_posix() for p in glob.glob(str(ROOT / "tests" / "examples" / "*.mzQC")))
# pymzqc normalises these on load (adds a timezone, drops non-schema keys or
# null values) whereas the viewer shows the file content as written.
PYMZQC_NORMALISED = {
    "tests/examples/individual-runs_creationDateNoTimezoneinfo.mzQC",
    "tests/examples/individual-runs_extraJSONcontent.mzQC",
    SHOWCASE,
}

DROP_IF_EMPTY_LIST = {"setQualities", "runQualities", "cvParameters", "fileProperties"}
DROP_IF_EMPTY_STRING = {"contactName", "contactAddress", "description"}


def readability2(obj):
    """Python statement of the elements pymzqc's readability=2 output omits."""
    if isinstance(obj, dict):
        return {k: readability2(v) for k, v in obj.items()
                if not ((k in DROP_IF_EMPTY_LIST and v == []) or (k in DROP_IF_EMPTY_STRING and v == ""))}
    if isinstance(obj, list):
        return [readability2(v) for v in obj]
    return obj


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


def open_viewer(page, base_url, path):
    page.goto(f"{base_url}/{VIEWER}/index.html?url={quote('/' + path)}")
    page.wait_for_selector("body.has-doc, .msg-error")


def test_core_unit_tests(page, base_url):
    page.goto(f"{base_url}/{VIEWER}/tests/index.html")
    results = page.evaluate("window.__testResults")
    failed = [r for r in results if not r["ok"]]
    assert results and not failed, failed


@pytest.mark.parametrize("path", EXAMPLES + [SHOWCASE])
def test_readability2_matches_python(page, base_url, path):
    open_viewer(page, base_url, path)
    assert page.locator(".msg-error").count() == 0
    shown = json.loads(page.evaluate("MzqcViewer.serialize()"))
    text = (ROOT / path).read_text()
    assert shown == readability2(json.loads(text))
    if path not in PYMZQC_NORMALISED:
        assert shown == json.loads(mzqc_io.to_json(mzqc_io.from_json(text), readability=2))


@pytest.mark.parametrize("path", [EXAMPLES[0], SHOWCASE])
def test_expanded_source_text_is_the_serialisation(page, base_url, path):
    open_viewer(page, base_url, path)
    page.evaluate("MzqcViewer.expandAll()")
    assert page.inner_text("#source") == page.evaluate("MzqcViewer.serialize()")


def test_highlighting_classes(page, base_url):
    open_viewer(page, base_url, SHOWCASE)
    page.evaluate("MzqcViewer.expandAll()")
    mzqc_keys = set(page.locator("#source .t-key-mzqc").all_inner_texts())
    data_keys = set(page.locator("#source .t-key-data").all_inner_texts())
    assert {'"qualityMetrics"', '"accession"', '"value"', '"unit"'} <= mzqc_keys
    # table column names below a metric value are data, not schema elements
    assert {'"MS:1000894"', '"m/z"', '"charge"'} <= data_keys
    assert page.locator("#source .t-accession", has_text='"MS:4000059"').count() >= 1
    assert page.locator("#source .t-number").count() > 100
    assert page.locator("#source .t-boolean").count() >= 1
    assert page.locator("#source .t-null").count() >= 1
    assert page.locator("#source .t-uri").count() >= 1


def test_large_arrays_start_collapsed_and_expand(page, base_url):
    open_viewer(page, base_url, SHOWCASE)
    rt_path = "/mzQC/runQualities/0/qualityMetrics/2/value/MS:1000894"
    fold = page.locator(f'details.fold[data-path="{rt_path}"]')
    assert not fold.evaluate("el => el.open")
    assert fold.locator(".kids > .ln").count() == 0  # children built lazily
    fold.locator(":scope > summary").click()
    sync_api.expect(fold.locator(":scope > .kids > .ln")).to_have_count(240)


def test_report_renders_metrics_tables_and_plots(page, base_url):
    open_viewer(page, base_url, SHOWCASE)
    report = page.locator("#report")
    assert report.locator("section.quality").count() == 2
    assert report.locator("article.metric").count() == 9
    assert report.locator(".badge-run").count() == 1 and report.locator(".badge-set").count() == 1
    # TIC table plotted as a line over retention time, precursor table as a scatter plot
    tic = report.locator('article.metric[data-path="/mzQC/runQualities/0/qualityMetrics/2"]')
    assert tic.locator("svg.plot path.plot-line").count() == 1
    precursors = report.locator('article.metric[data-path="/mzQC/runQualities/0/qualityMetrics/3"]')
    assert precursors.locator("svg.plot path.plot-dots").count() == 1
    assert precursors.locator(".plot-controls select").nth(1).input_value() == "intensity"
    assert precursors.locator("table.data tbody tr").count() == 60
    # switching the plot style redraws
    tic.locator(".plot-controls select").last.select_option("scatter")
    assert tic.locator("svg.plot path.plot-dots").count() == 1
    # scalar, range, vector and matrix renders
    assert report.locator(".big-num", has_text="5074").count() == 2
    assert report.locator(".range-dash").count() == 1
    assert report.locator(".value-chip").count() == 5
    vector = report.locator('article.metric[data-path="/mzQC/runQualities/0/qualityMetrics/4"]')
    assert vector.locator("svg.plot").count() == 1


def test_report_title_is_the_largest_text(page, base_url):
    open_viewer(page, base_url, SHOWCASE)
    sizes = page.evaluate("""() => {
        const px = el => parseFloat(getComputedStyle(el).fontSize);
        const title = document.querySelector('#report .report-head h2');
        const others = [...document.querySelectorAll('#report *')]
            .filter(el => el !== title && !title.contains(el) && el.offsetParent !== null)
            .map(px);
        return {title: px(title), largest_other: Math.max(...others)};
    }""")
    assert sizes["title"] >= sizes["largest_other"], sizes


def test_report_source_link_reveals_collapsed_node(page, base_url):
    open_viewer(page, base_url, SHOWCASE)
    page.evaluate("MzqcViewer.collapseAll()")
    path = "/mzQC/runQualities/0/qualityMetrics/3"
    page.locator(f'#report article.metric[data-path="{path}"] .source-link').click()
    target = page.locator(f'#source [data-path="{path}"]')
    assert target.evaluate("el => el.open")
    assert target.evaluate("el => el.classList.contains('flash')")


def test_two_panels_when_wide_tabs_when_narrow(page, base_url):
    open_viewer(page, base_url, EXAMPLES[0])
    assert page.locator("#source-panel").is_visible()
    assert page.locator("#report-panel").is_visible()
    assert not page.locator("#tabs").is_visible()
    page.click("#toggle-report")
    assert not page.locator("#report-panel").is_visible()
    page.click("#toggle-report")

    page.set_viewport_size({"width": 800, "height": 900})
    assert page.locator("#tabs").is_visible()
    assert not page.locator("#splitter").is_visible()
    assert page.locator("#source-panel").is_visible()
    assert not page.locator("#report-panel").is_visible()
    page.click('#tabs [data-tab="report"]')
    assert page.locator("#report-panel").is_visible()
    assert not page.locator("#source-panel").is_visible()
    # no horizontal page scroll at phone width
    page.set_viewport_size({"width": 375, "height": 800})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_source_panel_can_be_hidden(page, base_url):
    open_viewer(page, base_url, SHOWCASE)
    page.click("#toggle-source")
    assert not page.locator("#source-panel").is_visible()
    assert not page.locator("#splitter").is_visible()
    assert page.locator("#report-panel").bounding_box()["width"] > 1300
    # the last shown panel cannot be hidden as well
    assert page.locator("#toggle-report").is_disabled()
    # "{ } source" brings the source panel back
    page.locator("#report article.metric .source-link").first.click()
    assert page.locator("#source-panel").is_visible()
    assert page.get_attribute("#toggle-source", "aria-pressed") == "true"
    assert page.locator("#toggle-report").is_enabled()


def test_splitter_resizes_the_panels(page, base_url):
    open_viewer(page, base_url, SHOWCASE)

    def width(selector):
        return page.locator(selector).bounding_box()["width"]

    def drag_splitter_to(x):
        bar = page.locator("#splitter").bounding_box()
        y = bar["y"] + 200
        page.mouse.move(bar["x"] + bar["width"] / 2, y)
        page.mouse.down()
        page.mouse.move(x, y, steps=4)
        page.mouse.up()
        bar = page.locator("#splitter").bounding_box()
        return bar["x"] + bar["width"] / 2

    assert abs(width("#source-panel") - width("#report-panel")) < 2
    assert abs(drag_splitter_to(400) - 400) < 2
    assert width("#source-panel") < width("#report-panel")
    # each panel keeps a minimum width
    drag_splitter_to(5)
    assert abs(width("#source-panel") - 280) < 2
    drag_splitter_to(1395)
    assert abs(width("#report-panel") - 280) < 2
    # keyboard: Enter resets, arrows move in 2 % steps
    page.focus("#splitter")
    page.keyboard.press("Enter")
    assert page.get_attribute("#splitter", "aria-valuenow") == "50"
    page.keyboard.press("ArrowRight")
    assert page.get_attribute("#splitter", "aria-valuenow") == "52"
    assert width("#source-panel") > width("#report-panel")
    page.dblclick("#splitter")
    assert page.get_attribute("#splitter", "aria-valuenow") == "50"


def test_invalid_json_shows_error_with_position(page, base_url):
    page.goto(f"{base_url}/{VIEWER}/index.html")
    page.evaluate("""MzqcViewer.loadText('{\\n  "mzQC": {\\n    "version": 1.0.0\\n  }\\n}', 'broken.mzQC')""")
    error = page.locator(".msg-error")
    assert "line 3" in error.inner_text()
    assert not page.locator("#source").is_visible()


def test_non_mzqc_json_still_shows_source(page, base_url):
    page.goto(f"{base_url}/{VIEWER}/index.html")
    page.evaluate("""MzqcViewer.loadText('{"foo": [1, 2]}', 'other.json')""")
    assert page.locator(".msg-warn", has_text='No top level "mzQC"').count() == 1
    assert page.locator("#source .t-key-data", has_text='"foo"').count() == 1
