"""
Code content tests for mzQC versioning:
    * package
    * docs
    * examples
    * GH page
Runs only if explicitly required (pytest -v --checkversioning)
"""
__author__ = 'walzer'
import re
import pkg_resources
from collections import defaultdict
import pytest
from mzqc import MZQCFile as qc
from mzqc.MZQCFile import get_version_string

version = get_version_string()

def extract_version_and_check(line, ref_ver, no_v = False):
    """
    extract_version_and_check

    Assumes the given line is supposed to contain a version, this method will extract the version 
    (`r'v\d+\.\d+\.\d+'`) and check against the given version.

    Parameters
    ----------
    line : str
        The string supposed to contain a version sub-string
    ref_ver : str
        Given version to check against
    """
    matches = re.finditer(r'v\d+\.\d+\.\d+[rR][[cC]\d+]*', line)
    if no_v:
        matches = re.finditer(r'\d+\.\d+\.\d+[rR][[cC]\d+]*', line)

    if matches:
        for k in matches:
            if no_v:
                assert k.group(0) == ref_ver
            else:
                assert k.group(0)[1:] == ref_ver

    else:
        assert False

@pytest.mark.check_versioning
class TestVersions:
    """
    This is a final test to check if the versions used in the local tests match the version in main branch
    """
    def test_docs(self):
        with open("doc/source/conf.py", 'r') as fh:
            scpy = fh.readlines()
        for line in scpy:
            if "release =" in line:
                extract_version_and_check(line.strip(),version, no_v=False)

    def test_setup(self):
        with open("setup.py", 'r') as fh:
            scpy = fh.readlines()
        for line in scpy:
            if "version=" in line:
                extract_version_and_check(line.strip(),version, no_v=True)

    def test_accessories(self):
        for fn in ["mzqcaccessories/filehandling/mzqc_fileinfo.py","mzqcaccessories/filehandling/mzqc_filemerger.py", 
                   "mzqcaccessories/filehandling/mzqc_fixdescriptions.py","mzqcaccessories/offlinevalidator/mzqc_offline_validator.py"]:
            with open(fn, 'r') as fh:
                scpy = fh.readlines()
            for line in scpy:
                if "@click.version_option" in line:
                    extract_version_and_check(line.strip(),version, no_v=False)
