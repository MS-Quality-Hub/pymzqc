# How to build and release
(aka pre-filght tests for a release)

Packaging is declared in `pyproject.toml` and built with [hatchling](https://hatch.pypa.io/latest/).
There is no `setup.py`; every build goes through the PEP 517 frontend (`python3 -m build`).

## Release checklist

1. Choose the release version. Do **not** add a static package version to
   `pyproject.toml` or `doc/source/conf.py`: Hatch VCS derives the package
   version from Git tags, and the documentation reads the installed package
   version dynamically. `pytest --checkversioning` verifies the VCS setup and
   release-visible version consumers.
2. Run the pre-flight tests below from a full Git checkout with tags available.
3. Test the CI with a pull request and, for larger changes, a release candidate
   (see [Testing the CI before a release](#testing-the-ci-before-a-release)).
4. Publish a GitHub release tagged `vX.Y.Z` at the release commit. The tag is
   the package version source of truth.
   The `release-builds` workflow then builds the sdist and wheel, verifies their
   filenames match the release tag, builds the containers, and uploads the
   distributions to PyPI automatically (see [Automated release](#automated-release)).

## Manual build and pre-flight tests

First, for a given release candidate, work from a full clone so Hatch VCS can
see the version tags:
```bash
    cd /tmp
    git clone https://github.com/MS-Quality-hub/pymzqc.git
    cd pymzqc
    git fetch --tags
    python3 -m venv ../pipgit && source ../pipgit/bin/activate
    pip install pip --upgrade
    pip install -e ".[dev]"
    playwright install chromium   # browser for the viewer tests (tests/test_viewer.py)
```
The `dev` extra brings every optional feature plus the test, build and documentation tools.
Without Playwright or a Chromium build the viewer tests are skipped.

Re-activate your venv to let pytest reset to current venv and test installation: 
```bash
    deactivate && source /tmp/pipgit/bin/activate
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
    pip install pytest "$(ls dist/pymzqc-*-py3-none-any.whl)[onlinevalidator]"
    deactivate && source pipwhl/bin/activate
    cd /tmp/pymzqc
    pytest
```

Finally, run the versioning check, which is what the release workflow runs:
```bash
    pytest -v --checkversioning
```

## Automated release

Publishing a GitHub release (or pre-release) runs the `release-builds` workflow once.
It runs the unit tests, builds the sdist and wheel and checks that their file names
match the tag, builds both container images, smoke-tests them
(`.github/scripts/smoke-test-container.sh`) and pushes them to
[quay.io/mwalzer/pymzqc](https://quay.io/repository/mwalzer/pymzqc?tab=tags) and
[quay.io/mwalzer/mzqc-validator](https://quay.io/repository/mwalzer/mzqc-validator?tab=tags)
tagged with the release tag (and `latest`, except for pre-releases), and uploads
the distributions to TestPyPI and then PyPI.

The PyPI jobs authenticate with [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
(OIDC), so there is no API token stored in the repository.

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

### Testing the CI before a release

1. **Pull request.** Opening a pull request runs the `pullrequest-builds` workflow:
   unit tests on the oldest and newest supported Python, the viewer browser tests
   (non-blocking: failures only show as a warning), the wheel build, and both
   container images, built and smoke-tested and, when the quay.io secrets are
   available, pushed as `latest_pullrequest_build` and `<branch>_<sha>`.
2. **Release candidate.** Publishing a GitHub *pre-release* tagged `vX.Y.ZrcN`
   (e.g. `v1.1.0rc1`, without a hyphen, so that the tag matches the normalised
   package version) runs the complete release workflow. The candidate goes to
   TestPyPI and PyPI, where pip only installs it when asked for explicitly
   (`pip install pymzqc==1.1.0rc1` or `--pre`), and the images get the `vX.Y.ZrcN`
   tag without moving `latest`.

To smoke-test the images locally, build the wheel into the repository root as the
workflows do, then build and test each image (with podman, set `DOCKER=podman`):
```bash
    python3 -m build --wheel && cp dist/pymzqc-*-py3-none-any.whl .
    docker build -f containers/Dockerfile -t pymzqc-smoke-test .
    bash .github/scripts/smoke-test-container.sh pymzqc pymzqc-smoke-test
    docker build -f mzqcaccessories/onlinevalidator/Dockerfile -t validator-smoke-test .
    bash .github/scripts/smoke-test-container.sh validator validator-smoke-test
    rm pymzqc-*-py3-none-any.whl
```

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
    python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pymzqc==X.Y.Z
    deactivate && source pippypi/bin/activate
    cd /tmp/pymzqc
    pytest
```
Since the index-url probably won't have all dependency packages, install will fail unless you set extra-index-url.

Check the release label isn't already in use in pypi.org/pymzqc (otherwise correct,repeat build & test).
Now upload to pypi.org, fingers crossed.
