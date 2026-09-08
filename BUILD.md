# How to build and release
(aka pre-filght tests for a release)

Packaging is declared in `pyproject.toml` and built with [hatchling](https://hatch.pypa.io/latest/).
There is no `setup.py`; every build goes through the PEP 517 frontend (`python3 -m build`).

## Release checklist

1. Bump the version in **both** places and commit:
   * `pyproject.toml` (`version = "..."`)
   * `doc/source/conf.py` (`release = "v..."`)

   `pytest --checkversioning` is the gate that checks these agree with the
   version of the installed package.
2. Run the pre-flight tests below.
3. Publish a GitHub release tagged `vX.Y.Z`.
   The `release-builds` workflow then builds the sdist and wheel and uploads
   them to PyPI automatically (see [Automated release](#automated-release)).

## Manual build and pre-flight tests

First, for a given release (candidate), install a local version via `pip git+` and get the sources for test and build, too:
```bash
    cd /tmp
    python3 -m venv pipgit && source pipgit/bin/activate
    pip install pip --upgrade
    pip install pytest build
    pip install -U git+https://github.com/MS-Quality-hub/pymzqc.git@v1.0.0#egg=pymzqc
    git clone --single-branch --branch=v1.0.0 --depth=1 https://github.com/MS-Quality-hub/pymzqc.git
```

Re-activate your venv to let pytest reset to current venv and test installation: 
```bash
    deactivate && source pipgit/bin/activate
    cd /tmp/pymzqc
    pytest
```

Then build both distributions:
```bash 
    cd /tmp/pymzqc
    python3 -m build
```
The build results will be at `/tmp/pymzqc/dist`. We'll need both as release artifacts.
Now install the wheel in a new venv and test the wheel:
```bash
    cd /tmp/pymzqc
    deactivate
    python3 -m venv pipwhl && source pipwhl/bin/activate
    pip install pip --upgrade
    pip install pytest dist/pymzqc-1.0.0-py3-none-any.whl
    deactivate && source pipwhl/bin/activate
    cd /tmp/pymzqc
    pytest
```

Finally, run the versioning check, which is what the release workflow runs:
```bash
    pytest -v --checkversioning
```

## Automated release

Publishing a GitHub release runs the `release-builds` workflow, which runs the
unit tests, builds the sdist and wheel, builds the containers, and then uploads
the distributions to PyPI from the `publish-pypi` job.

That job authenticates with [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
(OIDC), so there is no API token stored in the repository. It only runs for the
`published` event, because the workflow also fires on `created` and `edited` and
re-uploading an existing file would fail.

This requires a one-time setup on pypi.org, under the `pymzqc` project's
*Publishing* settings, adding a trusted publisher with:

| Field             | Value                  |
|-------------------|------------------------|
| Owner             | `MS-Quality-Hub`       |
| Repository name   | `pymzqc`               |
| Workflow name     | `release_builds.yml`   |
| Environment name  | `pypi`                 |

Until that entry exists the `publish-pypi` job will fail at the authentication
step; the rest of the release workflow is unaffected.

### Publishing by hand

If you need to upload outside the workflow, build as above and use twine.
Test against test.pypi.org first:
```bash
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
And test that installation:
```bash    
    cd /tmp/pymzqc
    deactivate
    python3 -m venv pippypi && source pippypi/bin/activate
    pip install pip --upgrade
    pip install pytest
    python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pymzqc==1.0.0
    deactivate && source pippypi/bin/activate
    cd /tmp/pymzqc
    pytest
```
Since the index-url probably won't have all dependency packages, install will fail unless you set extra-index-url.

Check the release label isn't already in use in pypi.org/pymzqc (otherwise correct,repeat build & test).
Now upload to pypi.org, fingers crossed.
