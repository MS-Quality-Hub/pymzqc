How to build and release
========================
(aka pre-filght tests for a release)

Manual build instruction
""""""""""""""""""""""""
This file only exists to provide container-based builds an existing dist folder setup, i.e.:
.. code-block:: bash
    mkdir -p dist/mzqc
    python3 -m build --sdist
    python3 -m build --wheel

.. code-block:: bash
    python3 -m venv pipgit && source pipgit/bin/activate
    pip install pip --upgrade
    pip install pytest jsonschema pandas numpy pandas pronto==2.2.0 requests
    pip install -U git+https://github.com/MS-Quality-hub/pymzqc.git@v1.0.0rc1#egg=pymzqc
    cp -r pymzqc/tests /tmp/fake_mzqc_folder
    cd /tmp/fake_mzqc_folder
    pytest

.. code-block:: bash
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

test artifact installation:
.. code-block:: bash
    python3 -m venv pypitest && source pypitest/bin/activate
    pip install pip --upgrade
    pip install pytest jsonschema pandas numpy pandas pronto==2.2.0 requests
    pip install -i https://test.pypi.org/simple/ pymzqc==1.0.0rc1
    cp -r pymzqc/tests /tmp/fake_mzqc_folder
    cd /tmp/fake_mzqc_folder
    pytest



