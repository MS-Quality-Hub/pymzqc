__author__ = 'walzer'
import pytest  # Eeeeeeverything needs to be prefixed with test ito be picked up by pytest, i.e. TestClass() and test_function()
from mzqc import MZQCFile as qc
import numpy as np
from datetime import datetime
import pkg_resources
import re


"""
Code content tests for mzQC versioning
"""
version = pkg_resources.require("mzqc-pylib")[0].version  # main branch setup.py is _the_ reference for the version number

def extract_version_and_check(line, ref_ver):
    """
    extract_version_and_check

    Assumes the given line is supposed to contain a version, will extract the versions (r'v\d+\.\d+\.\d+') 
    and check against the given version.

    Parameters
    ----------
    line : str
        The string supposed to contain a version sub-string
    ref_ver : str
        Given version to check against
    """    
    matches = re.finditer('v\d+\.\d+\.\d+', line)
    if matches:
        for k in matches:
            assert k.group(0)[1:] == ref_ver
    else:
        assert False 


class TestVersions:
    def test_readme(self):
        with open("README.md", 'r') as fh:
            rmd = fh.readlines()
        for line in rmd:
            if "(https://mybinder.org/badge_logo.svg)" in line:
                extract_version_and_check(line,version)
            if "[interactive python notebook]" in line:
                extract_version_and_check(line,version)
       
    """
    This is a final test to check if the versions used in the local tests match the version in main branch
    """
    def test_docs(self):
        with open("doc/source/conf.py", 'r') as fh:
            scpy = fh.readlines()
        for line in scpy:
            if "release =" in line:
                extract_version_and_check(line.strip(),version)
        
