# How to build and release
(aka pre-filght tests for a release)

## Manual build and release instruction

First, install a local version of the release candidate installed via `pip git+` and get the sources for test and build, too:
```bash
    cd /tmp
    python3 -m venv pipgit && source pipgit/bin/activate
    pip install pip --upgrade
    pip install pytest build
    pip install -U git+https://github.com/MS-Quality-hub/pymzqc.git@v1.0.0rc1#egg=pymzqc
    git clone --single-branch --branch=v1.0.0rc1 --depth=1 https://github.com/MS-Quality-hub/pymzqc.git
```

Re-activate your venv to let pytest reset to current venv and test installation: 
```bash
    deactivate && source pipgit/bin/activate
    cd /tmp/pymzqc
    pytest
```

Then, provide container-based builds an existing dist folder setup like so, and build:
```bashcd 
    cd /tmp/pymzqc
    mkdir -p dist/mzqc
    python3 -m build --sdist
    python3 -m build --wheel
```
The build results will be at `/tmp/pymzqc/dist`. We'll need both as release artifacts.
Now install the wheel in a new venv and test the wheel:
```bash
    cd /tmp/pymzqc
    deactivate
    python3 -m venv pipwhl && source pipwhl/bin/activate
    pip install pip --upgrade
    pip install pytest wheel dist/pymzqc-1.0.0rc1-py3-none-any.whl
    deactivate && source pipwhl/bin/activate
    cd /tmp/pymzqc
    pytest
```

Also test wheel installation in legacy mode (w/o wheel module installed):
```bash
    cd /tmp/pymzqc
    deactivate
    python3 -m venv pipwhl && source pipwhl/bin/activate
    pip install pip --upgrade
    pip install pytest dist/pymzqc-1.0.0rc1-py3-none-any.whl
    deactivate && source pipwhl/bin/activate
    cd /tmp/pymzqc
    pytest
```

If all tests were successful, upload to test.pypi.org with twine:
```bash
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

And finally test pypi installation:
```    cd /tmp/pymzqc
    deactivate
    python3 -m venv pippypi && source pippypi/bin/activate
    pip install pip --upgrade
    pip install pytest
    python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pymzqc==1.0.0rc1
    deactivate && source pippypi/bin/activate
    cd /tmp/pymzqc
    pytest
```
Since the index-url probably won't have all dependency packages, install will fail unless you set extra-index-url.

Check the release label isn't already in use in pypi.org/pymzqc (otherwise correct,repeat build & test).
Now upload to pypi.org, fingers crossed.