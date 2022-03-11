__author__ = 'walzer'
import pytest  # Eeeeeeverything needs to be prefixed with test ito be picked up by pytest, i.e. TestClass() and test_function()
from mzqc import MZQCFile as qc
import tempfile

"""
Unit tests for I/O consistency of the library
"""

with open("tests/nameOfYourFile.mzQC", "r") as file:
    ref_str = file.read()

class TestCircle:

    def test_i_then_o(self):
        with open("tests/nameOfYourFile.mzQC", "r") as file:
            my_test_file = qc.JsonSerialisable.FromJson(file)   
            assert qc.JsonSerialisable.ToJson(my_test_file, readability=1) == ref_str 
        
    def test_o_then_i(self):
        with open("tests/nameOfYourFile.mzQC", "r") as file:
            to_out = qc.JsonSerialisable.FromJson(file)
            with tempfile.NamedTemporaryFile("w", delete=False) as tmp_file:
                tmp_file.write(qc.JsonSerialisable.ToJson(to_out))
            with open(tmp_file.name, "r") as reread_file:
                assert qc.JsonSerialisable.ToJson(to_out) == qc.JsonSerialisable.ToJson(qc.JsonSerialisable.FromJson(reread_file))