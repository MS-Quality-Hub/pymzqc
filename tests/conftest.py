import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--checkversioning", action="store_true", default=False, help="run check_versioning marked tests"
    )

def pytest_configure(config):
    config.addinivalue_line("markers", "check_versioning: mark test as versioning test (final check before release)")

def pytest_collection_modifyitems(config, items):
    if config.getoption("--checkversioning"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_versioning = pytest.mark.skip(reason="needs --checkversioning option to run")
    for item in items:
        if "check_versioning" in item.keywords:
            item.add_marker(skip_versioning)
