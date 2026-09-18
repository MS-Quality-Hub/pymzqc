"""
Code content tests for mzQC versioning:
    * package
    * docs
    * Hatch VCS configuration
    * CLI accessories
Runs only if explicitly required (pytest -v --checkversioning)
"""
__author__ = 'walzer'

import re
import runpy
from pathlib import Path

import pytest
from mzqc.MZQCFile import get_version_string


version = get_version_string()


@pytest.mark.check_versioning
class TestVersions:
    """Final checks for release-visible version consistency."""

    def test_docs(self):
        conf = runpy.run_path("doc/source/conf.py")
        assert conf["release"] == f"v{version}"

    def test_pyproject_uses_vcs_versioning(self):
        text = Path("pyproject.toml").read_text()

        project_match = re.search(
            r"(?ms)^\[project\]\s*$\n(.*?)(?=^\[|\Z)", text
        )
        assert project_match is not None
        project = project_match.group(1)
        assert re.search(
            r'(?m)^dynamic\s*=\s*\[\s*["\']version["\']\s*\]\s*$',
            project,
        )
        assert not re.search(r"(?m)^version\s*=", project)

        hatch_version_match = re.search(
            r"(?ms)^\[tool\.hatch\.version\]\s*$\n(.*?)(?=^\[|\Z)", text
        )
        assert hatch_version_match is not None
        assert re.search(
            r'(?m)^source\s*=\s*["\']vcs["\']\s*$',
            hatch_version_match.group(1),
        )

    def test_accessories_use_runtime_package_version(self):
        files = [
            "mzqcaccessories/filehandling/mzqc_fileinfo.py",
            "mzqcaccessories/filehandling/mzqc_filemerger.py",
            "mzqcaccessories/filehandling/mzqc_fixdescriptions.py",
            "mzqcaccessories/offlinevalidator/mzqc_offline_validator.py",
        ]
        for fn in files:
            version_lines = [
                line.strip()
                for line in Path(fn).read_text().splitlines()
                if "@click.version_option" in line
            ]
            assert version_lines, f"No click version option found in {fn}"
            assert all("get_version_string()" in line for line in version_lines)
