/*
 * mzqc-viewer.js — page logic of the mzQC viewer: file loading, the
 * highlighted, collapsible readability=2 source view, and the report panel.
 * Requires mzqc-core.js and mzqc-plot.js. Exposes `MzqcViewer` for tests.
 */
(function () {
  'use strict';
  const Core = window.MzqcCore;
  const Plot = window.MzqcPlot;
  const $ = (id) => document.getElementById(id);

  // Containers with more children than this start collapsed, and their
  // children are only built when first expanded.
  const LAZY_LIMIT = 50;
  // Table rows shown before "show all".
  const ROW_LIMIT = 100;
  // Above this many JSON nodes, "Expand all" asks first.
  const EXPAND_ALL_CONFIRM = 40000;
  // Narrowest a panel can be dragged with the splitter, in CSS pixels.
  const PANEL_MIN_WIDTH = 280;
  const OLS_URL = 'https://www.ebi.ac.uk/ols4/search?q=';

  const state = {
    name: '',
    tree: null,        // readability=2 node tree
    nodeCount: 0,
    report: null,
    lines: new Map(),  // JSON pointer -> rendered element (details or line div)
    picked: [],        // source lines of the plot point or heatmap cell last clicked
    split: 0.5,        // share of the wide layout given to the source panel
  };

  /* ------------------------------------------------------------------ */
  /* DOM helper                                                         */
  /* ------------------------------------------------------------------ */

  /** h('div', {class: 'x', text: 'y', onclick: fn}, child, ...) */
  function h(tag, attrs, ...children) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === undefined || v === null || v === false) continue;
      if (k === 'text') node.textContent = v;
      else if (k === 'class') node.className = v;
      else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v === true ? '' : v);
    }
    for (const c of children.flat()) {
      if (c === undefined || c === null || c === false) continue;
      node.append(c instanceof Node ? c : String(c));
    }
    return node;
  }

  const span = (cls, text) => h('span', { class: cls, text });
  const pointer = (path, seg) => `${path}/${String(seg).replace(/~/g, '~0').replace(/\//g, '~1')}`;

  /* ------------------------------------------------------------------ */
  /* Source view                                                        */
  /* ------------------------------------------------------------------ */

  function countNodes(node) {
    if (node.kind === 'object') return 1 + node.entries.reduce((s, e) => s + countNodes(e.value), 0);
    if (node.kind === 'array') return 1 + node.items.reduce((s, c) => s + countNodes(c), 0);
    return 1;
  }

  /** Leading part of a line: indentation and, for object members, the key. */
  function linePrefix(ctx) {
    const parts = [' '.repeat(ctx.depth * 4)];
    if (ctx.key !== null) {
      parts.push(span(`t-${Core.keyClass(ctx.key, ctx.insideValue)}`, JSON.stringify(ctx.key)));
      parts.push(span('t-punct', ': '));
    }
    return parts;
  }

  function renderNode(node, ctx) {
    const comma = ctx.last ? null : span('t-punct', ',');
    if (node.kind !== 'object' && node.kind !== 'array') {
      const cls = Core.valueClass(node, ctx.ownerKey);
      const text = node.kind === 'string' ? JSON.stringify(node.value) : node.kind === 'number' ? node.raw : String(node.value);
      const line = h('div', { class: 'ln', 'data-path': ctx.path }, linePrefix(ctx), span(`t-${cls}`, text), comma);
      state.lines.set(ctx.path, line);
      return line;
    }

    const isObject = node.kind === 'object';
    const children = isObject ? node.entries : node.items;
    const [open, close] = isObject ? ['{', '}'] : ['[', ']'];
    if (children.length === 0) {
      const line = h('div', { class: 'ln', 'data-path': ctx.path }, linePrefix(ctx), span('t-punct', open + close), comma);
      state.lines.set(ctx.path, line);
      return line;
    }

    const noun = isObject ? (children.length === 1 ? 'entry' : 'entries') : (children.length === 1 ? 'item' : 'items');
    const fold = h('details', { class: 'fold', 'data-path': ctx.path, style: `--d:${ctx.depth}` },
      h('summary', { class: 'ln' },
        linePrefix(ctx),
        span('t-punct', open),
        h('span', { class: 'fold-hint' },
          span('fold-count', ` ${children.length} ${noun} `), span('t-punct', close), comma && comma.cloneNode(true))),
      h('div', { class: 'kids' }),
      h('div', { class: 'ln' }, ' '.repeat(ctx.depth * 4), span('t-punct', close), comma));
    fold._build = () => {
      const kids = fold.querySelector(':scope > .kids');
      const insideValue = ctx.insideValue || ctx.key === 'value';
      const frag = document.createDocumentFragment();
      children.forEach((child, k) => {
        const key = isObject ? child.key : null;
        frag.append(renderNode(isObject ? child.value : child, {
          key,
          ownerKey: isObject ? key : ctx.ownerKey,
          depth: ctx.depth + 1,
          last: k === children.length - 1,
          path: pointer(ctx.path, isObject ? key : k),
          insideValue,
        }));
      });
      kids.append(frag);
      fold._build = null;
    };
    fold.addEventListener('toggle', () => { if (fold.open && fold._build) fold._build(); });
    if (children.length <= LAZY_LIMIT) {
      fold.open = true;
      fold._build();
    }
    state.lines.set(ctx.path, fold);
    return fold;
  }

  function renderSource(tree) {
    const code = $('source');
    code.textContent = '';
    state.lines.clear();
    state.picked = [];
    code.append(renderNode(tree, { key: null, ownerKey: null, depth: 0, last: true, path: '', insideValue: false }));
    code.hidden = false;
  }

  function openFold(fold) {
    if (fold._build) fold._build();
    fold.open = true;
  }

  function expandAll() {
    if (state.nodeCount > EXPAND_ALL_CONFIRM &&
        !window.confirm(`This file has ${state.nodeCount.toLocaleString()} JSON elements; expanding all may be slow. Continue?`)) {
      return;
    }
    let closed;
    while ((closed = $('source').querySelectorAll('details.fold:not([open])')).length) {
      closed.forEach(openFold);
    }
  }

  function collapseAll() {
    // Keep the document root and the mzQC object open, fold everything below.
    $('source').querySelectorAll('details.fold').forEach((fold) => {
      const depth = Number(fold.style.getPropertyValue('--d'));
      fold.open = depth < 2;
    });
  }

  /** Open every fold on the way to `path`; returns its element, if there is one. */
  function openPath(path) {
    const root = state.lines.get('');
    if (root && root.tagName === 'DETAILS') openFold(root);
    let prefix = '';
    for (const seg of path.split('/').slice(1)) {
      prefix += `/${seg}`;
      const node = state.lines.get(prefix);
      if (!node) break;
      if (node.tagName === 'DETAILS') openFold(node);
    }
    return state.lines.get(path);
  }

  function scrollToLine(target) {
    showTab('source');
    setPanelShown('source', true);
    const line = target.tagName === 'DETAILS' ? target.querySelector(':scope > summary') : target;
    line.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }

  /** Open every fold on the way to `path`, then scroll to and flash it. */
  function revealPath(path) {
    const target = openPath(path);
    if (!target) return;
    scrollToLine(target);
    target.classList.remove('flash');
    void target.offsetWidth; // restart the animation
    target.classList.add('flash');
  }

  /**
   * Mark the source lines of the values behind a plot point or heatmap cell
   * clicked in the report, until the next click, and scroll to the first.
   */
  function pickValues(paths) {
    state.picked.forEach((line) => line.classList.remove('picked'));
    state.picked = paths.map(openPath).filter(Boolean);
    state.picked.forEach((line) => line.classList.add('picked'));
    if (state.picked.length) scrollToLine(state.picked[0]);
  }

  /* ------------------------------------------------------------------ */
  /* Report view                                                        */
  /* ------------------------------------------------------------------ */

  const fmt = (v) => (typeof v === 'number' ? Core.formatNumber(v) : v === null ? 'null' : String(v));

  function sourceButton(path) {
    return h('button', {
      class: 'link-btn source-link', type: 'button', title: 'Show in source', 'data-path': path,
      onclick: () => revealPath(path),
    }, '{ } source');
  }

  function accessionChip(accession) {
    if (!accession) return null;
    return h('a', {
      class: 'chip', href: OLS_URL + encodeURIComponent(accession), target: '_blank', rel: 'noopener',
      title: 'Look up the term in the EBI Ontology Lookup Service',
    }, accession);
  }

  function safeLink(url, text) {
    if (typeof url === 'string' && /^(https?|ftp):\/\//i.test(url)) {
      return h('a', { href: url, target: '_blank', rel: 'noopener', text: text || url });
    }
    return document.createTextNode(text || url || '');
  }

  function dataTable(headers, rows, numericCols) {
    const table = h('table', { class: 'data' });
    if (headers) {
      table.append(h('thead', {}, h('tr', {}, headers.map((name, c) => h('th', { class: numericCols && numericCols[c] ? 'num' : null, text: name })))));
    }
    const body = h('tbody');
    const addRows = (from, to) => {
      const frag = document.createDocumentFragment();
      for (let r = from; r < to; r++) {
        frag.append(h('tr', {}, rows[r].map((v, c) => h('td', {
          class: typeof v === 'number' || (numericCols && numericCols[c]) ? 'num' : null,
          text: v === undefined ? '' : fmt(v),
        }))));
      }
      body.append(frag);
    };
    addRows(0, Math.min(rows.length, ROW_LIMIT));
    table.append(body);
    if (rows.length <= ROW_LIMIT) return h('div', { class: 'table-wrap' }, table);
    const more = h('button', {
      class: 'link-btn', type: 'button',
      onclick: () => { addRows(ROW_LIMIT, rows.length); more.remove(); },
    }, `Show all ${rows.length.toLocaleString()} rows`);
    return h('div', { class: 'table-wrap' }, table, more);
  }

  function plotBlock(columns, initial, onPick) {
    // columns: [{name, values}] numeric columns of equal length;
    // onPick(index, xName, yName), if given, is called for a clicked point
    const block = h('div', { class: 'plot-block' });
    const area = h('div', { class: 'plot-area' });
    const select = (label, value) => h('label', {}, `${label} `,
      h('select', {}, columns.map((c) => h('option', { value: c.name, selected: c.name === value }, c.name))));
    const xSel = select('x', initial.x);
    const ySel = select('y', initial.y);
    const modeSel = h('label', {}, 'style ', h('select', {},
      ['line', 'scatter'].map((m) => h('option', { value: m, selected: m === initial.mode }, m))));
    const draw = () => {
      const byName = (n) => columns.find((c) => c.name === n).values;
      const xName = xSel.querySelector('select').value;
      const yName = ySel.querySelector('select').value;
      Plot.render(area, {
        x: byName(xName), y: byName(yName), xLabel: xName, yLabel: yName,
        mode: modeSel.querySelector('select').value,
        onPick: onPick && ((k) => onPick(k, xName, yName)),
      });
    };
    const controls = h('div', { class: 'plot-controls' }, columns.length > 2 || initial.x !== 'index' ? [xSel, ySel] : [], modeSel);
    controls.addEventListener('change', draw);
    block.append(controls, area);
    draw();
    return block;
  }

  /** A fold whose content is built when it is first opened. */
  function lazyFold(summary, build, open) {
    const fold = h('details', { class: 'table-fold' }, h('summary', {}, summary));
    const fill = () => { if (fold.childElementCount === 1) fold.append(build()); };
    fold.addEventListener('toggle', () => { if (fold.open) fill(); });
    if (open) {
      fill();
      fold.open = true;
    }
    return fold;
  }

  function heatmapBlock(matrix, shape, unit, onPick) {
    const area = h('div', { class: 'plot-area' });
    const robust = Core.heatScale(matrix, true);
    const draw = (scale) => Plot.heatmap(area, { matrix, rows: shape.rows, cols: shape.cols, scale, label: unit, onPick });
    let controls = null;
    if (robust.clipped) {
      const select = h('select', {},
        h('option', { value: 'robust' }, '1st–99th percentile'),
        h('option', { value: 'full' }, 'min – max'));
      select.addEventListener('change', () => draw(select.value === 'robust' ? robust : Core.heatScale(matrix, false)));
      controls = h('div', { class: 'plot-controls' }, h('label', {}, 'colour range ', select));
    }
    draw(robust);
    return h('div', { class: 'plot-block' }, controls, area);
  }

  function renderValue(metric) {
    const { value, shape, unit } = metric;
    const unitSpan = unit ? span('unit', unit) : null;
    // JSON pointer of an element inside the value, e.g. at(column, row)
    const at = (...segments) => segments.reduce((path, seg) => pointer(path, seg), pointer(metric.path, 'value'));
    switch (shape.type) {
      case 'empty':
        return h('div', { class: 'metric-value muted' }, 'no value');
      case 'scalar':
        return h('div', { class: 'metric-value' },
          span(typeof value === 'number' ? 'big-num' : 'big-text', fmt(value)), unitSpan);
      case 'range':
        return h('div', { class: 'metric-value' },
          span('big-num', fmt(value[0])), span('range-dash', ' – '), span('big-num', fmt(value[1])), unitSpan);
      case 'vector': {
        const parts = [];
        if (value.length <= 12) {
          parts.push(h('div', { class: 'metric-value chips' }, value.map((v) => span('value-chip', fmt(v))), unitSpan));
        }
        if (shape.plottable) {
          parts.push(plotBlock(
            [{ name: 'index', values: value.map((_, k) => k) }, { name: unit || 'value', values: value }],
            { x: 'index', y: unit || 'value', mode: 'line' },
            (k) => pickValues([at(k)])));
        }
        if (value.length > 12) {
          parts.push(h('details', { class: 'table-fold' }, h('summary', {}, `Values (${value.length.toLocaleString()})`),
            dataTable(['#', unit || 'value'], value.map((v, k) => [k, v]))));
        }
        return h('div', {}, parts);
      }
      case 'table': {
        const names = shape.columns.map((c) => c.name);
        const rows = [];
        for (let r = 0; r < shape.rows; r++) rows.push(names.map((n) => value[n][r]));
        const table = dataTable(names, rows, shape.columns.map((c) => c.numeric));
        const caption = `Table (${shape.rows.toLocaleString()} rows × ${names.length} columns)`;
        if (!shape.plottable) return h('div', {}, h('div', { class: 'caption' }, caption, unitSpan), table);
        const numeric = shape.columns.filter((c) => c.numeric).map((c) => ({ name: c.name, values: value[c.name] }));
        // A point stands for a table row: mark the row's value in every column, the plotted y value first.
        const pickRow = (k, x, y) => pickValues([y, x, ...names.filter((n) => n !== x && n !== y)].map((n) => at(n, k)));
        return h('div', {},
          plotBlock(numeric, shape.plot, pickRow),
          h('details', { class: 'table-fold', open: shape.rows <= 20 }, h('summary', {}, caption), table));
      }
      case 'matrix': {
        const caption = `Matrix (${shape.rows.toLocaleString()} rows × ${shape.cols.toLocaleString()} columns)`;
        if (!shape.numeric) return h('div', {}, h('div', { class: 'caption' }, caption, unitSpan), dataTable(null, value));
        return h('div', {}, heatmapBlock(value, shape, unit, (r, c) => pickValues([at(r, c)])),
          lazyFold(caption, () => dataTable(null, value), shape.rows <= 20));
      }
      case 'record':
        return h('dl', { class: 'record' }, Object.entries(value).flatMap(([k, v]) => [h('dt', { text: k }), h('dd', { text: fmt(v) })]));
      default: {
        let text = JSON.stringify(value, null, 2);
        if (text.length > 4000) text = `${text.slice(0, 4000)}\n…`;
        return h('pre', { class: 'json-block', text });
      }
    }
  }

  function renderMetric(metric) {
    return h('article', { class: 'metric', 'data-path': metric.path },
      h('header', { class: 'metric-head' },
        h('h4', { text: metric.name }), accessionChip(metric.accession), sourceButton(metric.path)),
      metric.description ? h('p', { class: 'muted description', text: metric.description }) : null,
      renderValue(metric));
  }

  function renderQuality(q) {
    const files = q.inputFiles.length ? h('div', { class: 'table-wrap' }, h('table', { class: 'data files' },
      h('thead', {}, h('tr', {}, ['Input file', 'Format', 'Properties'].map((t) => h('th', { text: t })))),
      h('tbody', {}, q.inputFiles.map((f) => h('tr', {},
        h('td', {}, h('div', { class: 'file-title', text: f.name || '' }), h('div', { class: 'muted small' }, safeLink(f.location))),
        h('td', { text: (f.fileFormat && (f.fileFormat.name || f.fileFormat.accession)) || '' }),
        h('td', {}, (f.fileProperties || []).map((p) => h('div', { class: 'small' },
          span('muted', `${p.name || p.accession}: `), fmt(p.value === undefined ? '' : p.value)))))))))
      : null;
    const software = q.analysisSoftware.length ? h('ul', { class: 'software' }, q.analysisSoftware.map((s) => h('li', {},
      h('strong', { text: s.name || s.accession }), s.version ? ` ${s.version}` : '', ' ',
      accessionChip(s.accession), s.uri ? [' ', safeLink(s.uri)] : null))) : null;

    return h('section', { class: 'quality', id: `q-${q.kind}-${q.index}` },
      h('header', { class: 'quality-head' },
        span(`badge badge-${q.kind}`, q.kind === 'run' ? 'run' : 'set'),
        h('h3', { text: q.label }), sourceButton(q.path)),
      files,
      software ? h('div', { class: 'software-wrap' }, span('muted small', 'Analysis software'), software) : null,
      q.metrics.length ? q.metrics.map(renderMetric) : h('p', { class: 'muted', text: 'No quality metrics.' }));
  }

  function renderReport(report) {
    const panel = $('report');
    panel.textContent = '';
    if (!report.ok) {
      panel.append(h('p', { class: 'muted', text: 'No report: the document is not an mzQC file.' }));
      return;
    }
    const { meta } = report;
    const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;
    const runs = report.qualities.filter((q) => q.kind === 'run').length;
    const sets = report.qualities.length - runs;
    const facts = [
      ['mzQC version', meta.version],
      ['Created', meta.creationDate],
      ['Contact', meta.contactName],
      ['Contact address', meta.contactAddress],
      ['Content', `${plural(runs, 'run')}, ${plural(sets, 'set')}, ${plural(report.metricCount, 'metric')}`],
    ].filter(([, v]) => v);

    const toc = report.qualities.length > 1 ? h('nav', { class: 'toc' }, span('muted small', 'Jump to'),
      report.qualities.map((q) => h('a', { href: `#q-${q.kind}-${q.index}`, text: q.label }))) : null;

    panel.append(
      h('header', { class: 'report-head' },
        h('h2', { text: state.name || 'mzQC report' }),
        meta.description ? h('p', { class: 'description', text: meta.description }) : null,
        h('dl', { class: 'facts' }, facts.flatMap(([k, v]) => [h('dt', { text: k }), h('dd', { text: v })])),
        report.controlledVocabularies.length ? h('div', { class: 'cvs' }, span('muted small', 'Controlled vocabularies'),
          h('ul', {}, report.controlledVocabularies.map((cv) => h('li', {},
            safeLink(cv.uri, cv.name || cv.uri), cv.version ? span('muted', ` ${cv.version}`) : null)))) : null,
        toc),
      ...report.qualities.map(renderQuality));
  }

  /* ------------------------------------------------------------------ */
  /* Loading                                                            */
  /* ------------------------------------------------------------------ */

  function showMessages(items) {
    const box = $('messages');
    box.textContent = '';
    for (const { level, text, detail } of items) {
      box.append(h('div', { class: `msg msg-${level}`, role: level === 'error' ? 'alert' : null },
        h('div', { text }), detail ? h('pre', { text: detail }) : null));
    }
  }

  function errorSnippet(text, err) {
    const lines = text.split('\n');
    const from = Math.max(0, err.line - 3);
    const to = Math.min(lines.length, err.line + 1);
    const out = [];
    for (let k = from; k < to; k++) {
      out.push(`${String(k + 1).padStart(5)} | ${lines[k].slice(0, 200)}`);
      if (k + 1 === err.line) out.push(`${' '.repeat(8 + Math.min(err.column - 1, 200))}^`);
    }
    return out.join('\n');
  }

  function loadText(text, name) {
    state.name = name || '';
    $('file-name').textContent = state.name;
    document.title = state.name ? `${state.name} · mzQC Viewer` : 'mzQC Viewer';
    $('empty-state').hidden = true;
    let parsed;
    try {
      parsed = Core.parse(text);
    } catch (err) {
      state.tree = null;
      $('source').hidden = true;
      $('report').textContent = '';
      document.body.classList.remove('has-doc');
      const detail = err instanceof Core.ParseError ? errorSnippet(text, err) : null;
      showMessages([{ level: 'error', text: `Could not read the file as JSON: ${err.message}`, detail }]);
      return false;
    }
    state.tree = Core.readability2(parsed.root);
    state.nodeCount = countNodes(state.tree);
    state.report = Core.buildReport(Core.toPlain(state.tree));
    showMessages(parsed.warnings.concat(state.report.warnings).map((w) => ({ level: 'warn', text: w })));
    renderSource(state.tree);
    renderReport(state.report);
    document.body.classList.add('has-doc');
    return true;
  }

  async function loadFile(file) {
    try {
      loadText(await file.text(), file.name);
    } catch (err) {
      showMessages([{ level: 'error', text: `Could not open ${file.name}: ${err.message}` }]);
    }
  }

  async function loadUrl(url) {
    const name = decodeURIComponent(url.split(/[?#]/)[0].split('/').pop() || url);
    try {
      const resp = await fetch(url);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      loadText(await resp.text(), name);
    } catch (err) {
      $('empty-state').hidden = false;
      showMessages([{ level: 'error', text: `Could not load ${url}: ${err.message}` }]);
    }
  }

  function download() {
    if (!state.tree) return;
    const blob = new Blob([`${Core.serialize(state.tree)}\n`], { type: 'application/json' });
    const a = h('a', { href: URL.createObjectURL(blob), download: state.name || 'document.mzQC' });
    document.body.append(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  /* ------------------------------------------------------------------ */
  /* Layout                                                             */
  /* ------------------------------------------------------------------ */

  function showTab(tab) {
    $('main').dataset.tab = tab;
    document.querySelectorAll('#tabs [role=tab]').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.tab === tab)));
  }

  /** Show or hide a panel of the wide layout ('source' or 'report'). */
  function setPanelShown(panel, shown) {
    const main = $('main');
    main.classList.toggle(`no-${panel}`, !shown);
    for (const [name, other] of [['source', 'report'], ['report', 'source']]) {
      const button = $(`toggle-${name}`);
      button.setAttribute('aria-pressed', String(!main.classList.contains(`no-${name}`)));
      // Hiding both would leave an empty page, so the last shown panel stays.
      button.disabled = main.classList.contains(`no-${other}`);
    }
  }

  /** Give the source panel `share` (0..1) of the wide layout, the report the rest. */
  function setSplit(share) {
    const main = $('main');
    const width = main.clientWidth - $('splitter').offsetWidth;
    const min = Math.min(0.5, PANEL_MIN_WIDTH / Math.max(width, 1));
    state.split = Math.min(1 - min, Math.max(min, share));
    main.style.setProperty('--source-fr', `${state.split * 100}fr`);
    main.style.setProperty('--report-fr', `${(1 - state.split) * 100}fr`);
    const percent = Math.round(state.split * 100);
    $('splitter').setAttribute('aria-valuenow', String(percent));
    $('splitter').setAttribute('aria-valuetext', `Source ${percent} %, Report-Style ${100 - percent} %`);
  }

  function initSplitter() {
    const bar = $('splitter');
    bar.addEventListener('pointerdown', (ev) => {
      if (ev.button !== 0) return;
      ev.preventDefault();
      bar.focus();
      bar.setPointerCapture(ev.pointerId);
      document.body.classList.add('resizing');
      const box = $('main').getBoundingClientRect();
      const move = (e) => setSplit((e.clientX - box.left - bar.offsetWidth / 2) / (box.width - bar.offsetWidth));
      const end = () => {
        document.body.classList.remove('resizing');
        bar.removeEventListener('pointermove', move);
        bar.removeEventListener('pointerup', end);
        bar.removeEventListener('pointercancel', end);
      };
      bar.addEventListener('pointermove', move);
      bar.addEventListener('pointerup', end);
      bar.addEventListener('pointercancel', end);
    });
    bar.addEventListener('dblclick', () => setSplit(0.5));
    bar.addEventListener('keydown', (ev) => {
      const step = ev.shiftKey ? 0.1 : 0.02;
      const target = { ArrowLeft: state.split - step, ArrowRight: state.split + step, Home: 0, End: 1, Enter: 0.5 }[ev.key];
      if (target === undefined) return;
      ev.preventDefault();
      setSplit(target);
    });
  }

  function init() {
    $('file-input').addEventListener('change', (ev) => {
      if (ev.target.files[0]) loadFile(ev.target.files[0]);
      ev.target.value = '';
    });
    $('expand-all').addEventListener('click', expandAll);
    $('collapse-all').addEventListener('click', collapseAll);
    $('download').addEventListener('click', download);
    for (const panel of ['source', 'report']) {
      $(`toggle-${panel}`).addEventListener('click', () => setPanelShown(panel, $('main').classList.contains(`no-${panel}`)));
    }
    initSplitter();
    document.querySelectorAll('#tabs [role=tab]').forEach((b) => b.addEventListener('click', () => showTab(b.dataset.tab)));
    showTab('source');

    // Drag and drop anywhere on the page.
    let depth = 0;
    window.addEventListener('dragenter', (ev) => { ev.preventDefault(); depth++; document.body.classList.add('dragging'); });
    window.addEventListener('dragleave', () => { if (--depth <= 0) { depth = 0; document.body.classList.remove('dragging'); } });
    window.addEventListener('dragover', (ev) => ev.preventDefault());
    window.addEventListener('drop', (ev) => {
      ev.preventDefault();
      depth = 0;
      document.body.classList.remove('dragging');
      const file = ev.dataTransfer && ev.dataTransfer.files[0];
      if (file) loadFile(file);
    });

    const url = new URLSearchParams(window.location.search).get('url');
    if (url) loadUrl(url);
  }

  window.MzqcViewer = {
    loadText, loadUrl, expandAll, collapseAll, revealPath, showTab, setPanelShown, setSplit,
    serialize: () => (state.tree ? Core.serialize(state.tree) : ''),
    state,
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
