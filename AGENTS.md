# Notes for coding agents

pymzqc is the Python reference library for the PSI mzQC format (JSON quality-control files for mass
spectrometry), plus command-line accessories and a browser viewer. Human-facing docs: `README.md`,
`BUILD.md`, `doc/`. This file holds what an agent needs on top of those.

## Commands
Run everything from the repository root.

```bash
pip install -e ".[dev]"            # library + online validator deps + pytest, Playwright, build, Sphinx
playwright install chromium        # once; the viewer tests skip without a browser
pytest                             # whole suite; ~5 s
pytest tests/test_viewer.py        # viewer only (headless Chromium)
pytest --checkversioning           # also the release-time version checks (skipped by default)
flake8 . --select=E9,F63,F7,F82    # the lint CI treats as relevant
python -m build --wheel            # check packaging changes; inspect with: unzip -l dist/*.whl
sphinx-build -b html doc/source /tmp/pymzqc-docs   # graphviz needed for the class diagrams
```

The viewer tests launch Playwright's Chromium and fall back to any Chromium build cached under
`~/.cache/ms-playwright`, so a Playwright/browser version mismatch is not a reason to skip them.
In CI they run only on pull requests, in a separate `viewer-tests` job (`pullrequest_builds.yml`)
that only raises a warning on failure; the main test jobs do not install Playwright and skip them.

## Layout
- `mzqc/` – the library: `MZQCFile.py` (object model, JSON (de)serialisation), `SyntaxCheck.py`
  (JSON schema), `SemanticCheck.py` (CV and content checks).
- `mzqcaccessories/` – shipped in the same wheel: `offlinevalidator/`, `filehandling/` (click CLIs),
  `onlinevalidator/` (Flask API, also serves the viewer at `/viewer/`), `viewer/` (static HTML/JS).
- `tests/` – pytest suite. The `.mzQC` files in `tests/` and `tests/examples/` are fixtures whose exact
  content tests depend on (expected validation issues, round-trip output), so add new example files
  rather than editing existing ones.
- `doc/source/` – Sphinx (alabaster theme); most pages include the READMEs via MyST.

## Rules
- **Python 3.10 compatibility** for everything under `mzqc/` and `mzqcaccessories/`
  (`requires-python = ">=3.10"`, CI runs 3.10–3.14): nothing newer than 3.10, e.g. no `tomllib`,
  `typing.Self`, `except*` or `ExceptionGroup` (3.11), no `type X = ...` aliases or `def f[T]()`
  generics (3.12). A local venv may be much newer, so passing tests locally does not prove this.
- **mzQC names stay camelCase.** Class attributes and `__init__` parameters mirror the JSON schema
  element names (`runQualities`, `fileFormat`, …); `from_json` relies on parameter name == attribute
  name. Do not "fix" them to snake_case or rename them.
- **Serialisation is a contract.** `MzQcFile.to_json(readability=1)` is the canonical layout
  (`tests/test_rw_circle.py` round-trips it); `readability=2` (4-space indent, empty optional elements
  removed by the regexes at the end of `to_json`) is what the viewer reproduces. Do not depend on how
  `json.JSONEncoder.iterencode` chunks its output; it differs between CPython versions (see commit
  b5e1ce8).
- **Versions come from git tags** (hatch-vcs). Never write a version number into `pyproject.toml` or
  code; CI checkouts need `fetch-depth: 0`.
- **Extras only add dependencies.** Every `[project.scripts]` entry is installed with the base package;
  Python packaging cannot gate a script on an extra. An accessory with optional dependencies imports
  them in `try/except ImportError` and raises an `ImportError` naming the install command
  (`pip install pymzqc[onlinevalidator]`). Do not add an extra that has no dependencies.
- Wheel contents are controlled by `[tool.hatch.build.targets.wheel]` in `pyproject.toml`: new
  non-runtime files under `mzqcaccessories/` (Dockerfiles, test pages, scratch scripts) must be added
  to its `exclude` list. Check with `unzip -l` after building.
- Keep `doc/source/requirements.txt` (used by Read the Docs) in step with the base dependencies and the
  documentation part of the `dev` extra.
- Line length up to 127 (the flake8 setting in CI). No formatter is enforced; do not reformat code you
  are not changing.

## Viewer (`mzqcaccessories/viewer/`)
- Plain HTML, CSS and classic `<script>` JavaScript: no dependencies, no build step, no ES modules,
  no CDN. It must keep working when `index.html` is opened from disk (`file://`), from the Flask app,
  and from the docs site.
- `mzqc-core.js` is DOM-free and mirrors pymzqc's `readability=2` output; when the pruning rules in
  `MZQCFile.to_json` change, change `readability2()` there too. `tests/test_viewer.py` compares both
  for every example file (`PYMZQC_NORMALISED` lists files where pymzqc deliberately rewrites values).
- The Sphinx build copies the viewer into the docs (`copy_viewer` in `doc/source/conf.py`); a new
  viewer file must be added to `VIEWER_FILES` there.
- UI text uses the existing labels ("Report-Style", "Source"); check both the wide two-panel layout
  (≥1100 px) and the narrow tabbed layout when changing the page.

## Docs
- Section titles in the included READMEs become Sphinx labels (`autosectionlabel`); a README heading
  that matches a page title causes a duplicate-label warning. Rename the README heading instead.
- Relative links inside READMEs that point to other Markdown files give `myst.xref_missing` warnings
  in Sphinx; these are known and harmless.

## Working in this repo
- Do not commit local scratch or prompt files (e.g. `*_prompt.txt`) or anything under `doc/build/`,
  `dist/` or `.venv/`.
- Before calling a change done, run `pytest`; for packaging changes also build the wheel and look at
  its file list and `METADATA`; for docs or viewer changes look at the result in a browser.

## Commits
- Keep commits reasonably scoped and sized: one task, or a very few closely related ones, per commit.
  A commit carries its own test additions and test fixes, and the docs/README lines that describe it.
- Commit as you go; when several unrelated tasks are pending, split them into separate commits (stage
  per file or per hunk) instead of one catch-all commit.
- Each commit should leave the test suite passing.
- Work that was never committed may be committed in its final form; there is no need to replay
  intermediate attempts or reverted ideas.
- Message: a short imperative subject line (≤ 72 characters), a blank line, then a body saying what
  changed and why when that is not obvious from the subject.
