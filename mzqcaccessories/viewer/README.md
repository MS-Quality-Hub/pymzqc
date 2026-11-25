## mzQC viewer

A browser page to read mzQC files. Open a file with the button, or drop it onto the page.
The file is read by the browser only; nothing is uploaded.

- **Source panel**: the file pretty-printed like pymzqc's `readability=2` output
  (4-space indentation, empty optional elements such as `"description": ""` or `"cvParameters": []` removed).
  Colours tell element kinds apart: mzQC schema elements, data keys (e.g. table column names), strings,
  CV accessions, URIs, numbers, booleans and `null`, and structural punctuation.
  Every object and array folds; arrays with more than 50 entries start folded and are built only when opened.
  **Download** saves the text exactly as shown.
- **Report panel**: a rendered summary of the file: metadata, controlled vocabularies, and one section per
  run or set with its input files, analysis software and metrics. Single values, ranges, value lists,
  tables and matrices each get a fitting display. Tables with two or more numeric columns of equal length,
  and numeric value lists, are plotted (line plot when the x column is sorted, otherwise scatter), with
  selectable columns. Numeric matrices, such as the pixel images of imaging metrics (e.g. MS:4000228), are
  drawn as heatmaps: shades of blue for magnitudes, or blue–grey–red centred on 0 when the values lie on both
  sides of 0; `null` cells stay blank. The colours span the 1st to 99th percentile so that a few outlier cells
  do not wash out the rest (switchable to min – max). Hover over a cell, or focus the heatmap and use the
  arrow keys, to read its value; the numbers are also in a table below. **{ } source** jumps to the metric in
  the source panel.
- On wide windows (at least 1100 px) both panels are shown side by side, like a markdown preview;
  narrower windows switch between them with tabs. Drag the bar between the panels (or focus it and use
  the arrow keys) to change their widths; double-click it to reset. The **Source** and **Report-Style**
  buttons hide or show either panel.
- `index.html?url=<address>` opens a file from the web (the server must allow cross-origin requests).

### Running it
The viewer is plain HTML, CSS and JavaScript with no dependencies and no build step:

- open `index.html` straight from disk, or
- copy this folder to any static web host (for example GitHub Pages; only `index.html`,
  `mzqc-viewer.css` and the three `mzqc-*.js` files are needed), or
- run `mzqc-onlinevalidator` (`pip install "pymzqc[onlinevalidator]"`) and browse to
  `http://127.0.0.1:5000/viewer/`.

### Code layout
| File | Purpose |
|---|---|
| `mzqc-core.js` | DOM-free logic: JSON parser that keeps number text as written, the readability=2 transform, serialisation, highlight classes, report model, heatmap colour ranges |
| `mzqc-plot.js` | small SVG line/scatter plots and canvas heatmaps (colours from the `--heat-*` ramps in `mzqc-viewer.css`) |
| `mzqc-viewer.js` | page logic: loading, source view, report view, layout |
| `tests/` | `tests/index.html` runs the unit tests of `mzqc-core.js` in a browser; `fixtures/showcase.mzQC` exercises every value display |

The Python test suite drives the viewer in headless Chromium (`tests/test_viewer.py`, needs
`pip install "pymzqc[dev]"` and `playwright install chromium`). It checks that the shown document equals
pymzqc's `readability=2` output for the example files, as well as the highlighting, folding, report and layout.

The viewer shows the file as written: unlike pymzqc it does not add a missing timezone to `creationDate`
or drop elements that are not in the schema. Strings keep non-ASCII characters (Python escapes them as `\uXXXX`).
