/*
 * mzqc-core.js — DOM-free logic of the mzQC viewer.
 *
 * - parse():          JSON parser that keeps the source text of numbers, so the
 *                     viewer shows values exactly as written in the file.
 * - readability2():   drops the empty optional elements that pymzqc's
 *                     `to_json(..., readability=2)` removes.
 * - serialize():      4-space indented text, the layout of readability=2.
 * - buildReport():    turns the parsed document into a report model
 *                     (runs/sets, metrics, value shapes for tables and plots).
 *
 * Loaded as a classic script (exposes `MzqcCore`) so the viewer also works
 * when index.html is opened straight from disk.
 */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    root.MzqcCore = api;
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* Parsing                                                            */
  /* ------------------------------------------------------------------ */

  class ParseError extends Error {
    constructor(message, offset, line, column) {
      super(`${message} (line ${line}, column ${column})`);
      this.name = 'ParseError';
      this.offset = offset;
      this.line = line;
      this.column = column;
    }
  }

  const STRING_RE = /"(?:[^"\\\u0000-\u001f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"/y;
  const NUMBER_RE = /-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/y;
  // Python's json module writes these for float('nan') / float('inf'); pandas
  // backed metrics can contain them, so accept them and flag a warning.
  const NON_STANDARD_NUMBERS = [['-Infinity', -Infinity], ['Infinity', Infinity], ['NaN', NaN]];

  /**
   * Parse JSON text into a node tree.
   * Nodes: {kind:'object', entries:[{key, value}]}, {kind:'array', items:[]},
   *        {kind:'string', value}, {kind:'number', raw, value},
   *        {kind:'boolean', value}, {kind:'null', value:null}
   * @returns {{root: object, warnings: string[]}}
   */
  function parse(text) {
    let i = 0;
    const n = text.length;
    const warnings = [];
    if (text.charCodeAt(0) === 0xfeff) i = 1; // byte order mark

    function position(at) {
      let line = 1;
      let lineStart = 0;
      for (let k = 0; k < at && k < n; k++) {
        if (text.charCodeAt(k) === 10) {
          line++;
          lineStart = k + 1;
        }
      }
      return { line, column: at - lineStart + 1 };
    }

    function fail(message, at = i) {
      const { line, column } = position(at);
      throw new ParseError(message, at, line, column);
    }

    function skipWhitespace() {
      while (i < n) {
        const c = text.charCodeAt(i);
        if (c === 32 || c === 9 || c === 10 || c === 13) i++;
        else break;
      }
    }

    function readString() {
      STRING_RE.lastIndex = i;
      const m = STRING_RE.exec(text);
      if (!m) fail('Invalid string');
      i += m[0].length;
      return JSON.parse(m[0]);
    }

    function readValue() {
      skipWhitespace();
      if (i >= n) fail('Unexpected end of input');
      const c = text[i];
      if (c === '{') return readObject();
      if (c === '[') return readArray();
      if (c === '"') return { kind: 'string', value: readString() };
      if (text.startsWith('true', i)) { i += 4; return { kind: 'boolean', value: true }; }
      if (text.startsWith('false', i)) { i += 5; return { kind: 'boolean', value: false }; }
      if (text.startsWith('null', i)) { i += 4; return { kind: 'null', value: null }; }
      for (const [word, value] of NON_STANDARD_NUMBERS) {
        if (text.startsWith(word, i)) {
          const { line } = position(i);
          warnings.push(`Non-standard JSON number ${word} on line ${line}`);
          i += word.length;
          return { kind: 'number', raw: word, value };
        }
      }
      if (c === '-' || (c >= '0' && c <= '9')) {
        NUMBER_RE.lastIndex = i;
        const m = NUMBER_RE.exec(text);
        if (!m) fail('Invalid number');
        i += m[0].length;
        return { kind: 'number', raw: m[0], value: Number(m[0]) };
      }
      return fail(`Unexpected character '${c}'`);
    }

    function readObject() {
      const start = i;
      i++; // {
      const entries = [];
      const seen = new Set();
      skipWhitespace();
      if (text[i] === '}') { i++; return { kind: 'object', entries }; }
      for (;;) {
        skipWhitespace();
        if (text[i] !== '"') fail('Expected a property name in double quotes');
        const keyAt = i;
        const key = readString();
        if (seen.has(key)) {
          warnings.push(`Duplicate key "${key}" on line ${position(keyAt).line}`);
        }
        seen.add(key);
        skipWhitespace();
        if (text[i] !== ':') fail("Expected ':' after property name");
        i++;
        entries.push({ key, value: readValue() });
        skipWhitespace();
        if (text[i] === ',') { i++; continue; }
        if (text[i] === '}') { i++; return { kind: 'object', entries }; }
        if (i >= n) fail(`Unclosed object starting on line ${position(start).line}`);
        fail("Expected ',' or '}' in object");
      }
    }

    function readArray() {
      const start = i;
      i++; // [
      const items = [];
      skipWhitespace();
      if (text[i] === ']') { i++; return { kind: 'array', items }; }
      for (;;) {
        items.push(readValue());
        skipWhitespace();
        if (text[i] === ',') { i++; continue; }
        if (text[i] === ']') { i++; return { kind: 'array', items }; }
        if (i >= n) fail(`Unclosed array starting on line ${position(start).line}`);
        fail("Expected ',' or ']' in array");
      }
    }

    const rootNode = readValue();
    skipWhitespace();
    if (i < n) fail('Unexpected content after the JSON document');
    return { root: rootNode, warnings };
  }

  /* ------------------------------------------------------------------ */
  /* readability=2 transform and serialisation                          */
  /* ------------------------------------------------------------------ */

  // The optional elements pymzqc drops when they are empty (see the regular
  // expressions at the end of JsonSerialisable.to_json in mzqc/MZQCFile.py).
  const DROP_IF_EMPTY_ARRAY = new Set(['setQualities', 'runQualities', 'cvParameters', 'fileProperties']);
  const DROP_IF_EMPTY_STRING = new Set(['contactName', 'contactAddress', 'description']);

  /** Return a copy of the tree without empty optional elements. */
  function readability2(node) {
    if (node.kind === 'object') {
      const entries = [];
      for (const { key, value } of node.entries) {
        if (DROP_IF_EMPTY_ARRAY.has(key) && value.kind === 'array' && value.items.length === 0) continue;
        if (DROP_IF_EMPTY_STRING.has(key) && value.kind === 'string' && value.value === '') continue;
        entries.push({ key, value: readability2(value) });
      }
      return { kind: 'object', entries };
    }
    if (node.kind === 'array') {
      return { kind: 'array', items: node.items.map(readability2) };
    }
    return node;
  }

  /** Text of a scalar node as it appears in the serialised document. */
  function scalarText(node) {
    switch (node.kind) {
      case 'string': return JSON.stringify(node.value);
      case 'number': return node.raw;
      case 'boolean': return node.value ? 'true' : 'false';
      default: return 'null';
    }
  }

  /** Serialise with Python json.dumps(indent=4) layout. */
  function serialize(node, indent = 4) {
    const out = [];
    const pad = (depth) => ' '.repeat(depth * indent);
    function write(value, depth) {
      if (value.kind === 'object') {
        if (value.entries.length === 0) { out.push('{}'); return; }
        out.push('{\n');
        value.entries.forEach(({ key, value: child }, k) => {
          out.push(pad(depth + 1), JSON.stringify(key), ': ');
          write(child, depth + 1);
          out.push(k < value.entries.length - 1 ? ',\n' : '\n');
        });
        out.push(pad(depth), '}');
      } else if (value.kind === 'array') {
        if (value.items.length === 0) { out.push('[]'); return; }
        out.push('[\n');
        value.items.forEach((child, k) => {
          out.push(pad(depth + 1));
          write(child, depth + 1);
          out.push(k < value.items.length - 1 ? ',\n' : '\n');
        });
        out.push(pad(depth), ']');
      } else {
        out.push(scalarText(value));
      }
    }
    write(node, 0);
    return out.join('');
  }

  /** Convert a node tree to plain JavaScript values. */
  function toPlain(node) {
    if (node.kind === 'object') {
      const obj = {};
      for (const { key, value } of node.entries) obj[key] = toPlain(value);
      return obj;
    }
    if (node.kind === 'array') return node.items.map(toPlain);
    return node.value;
  }

  /* ------------------------------------------------------------------ */
  /* Highlighting classes                                               */
  /* ------------------------------------------------------------------ */

  // Property names defined by the mzQC schema (v1.0.0).
  const MZQC_KEYS = new Set([
    'mzQC', 'version', 'creationDate', 'contactName', 'contactAddress', 'description',
    'runQualities', 'setQualities', 'controlledVocabularies',
    'metadata', 'qualityMetrics', 'label', 'inputFiles', 'analysisSoftware', 'cvParameters',
    'location', 'name', 'fileFormat', 'fileProperties',
    'accession', 'value', 'unit', 'uri',
  ]);

  const ACCESSION_RE = /^[A-Za-z][A-Za-z0-9_]*:[A-Za-z0-9_.-]+$/;
  const URI_KEYS = new Set(['uri', 'location']);

  /**
   * Classify a property name. Keys below a metric `value` are data (e.g. table
   * column names), not schema elements, even if they share a name.
   */
  function keyClass(key, insideValue) {
    return !insideValue && MZQC_KEYS.has(key) ? 'key-mzqc' : 'key-data';
  }

  /** Classify a scalar for colouring. `key` is the owning property, if any. */
  function valueClass(node, key) {
    switch (node.kind) {
      case 'string':
        if (key === 'accession' && ACCESSION_RE.test(node.value)) return 'accession';
        if (URI_KEYS.has(key)) return 'uri';
        if (key === 'creationDate') return 'date';
        return 'string';
      case 'number': return 'number';
      case 'boolean': return 'boolean';
      default: return 'null';
    }
  }

  /* ------------------------------------------------------------------ */
  /* Report model                                                       */
  /* ------------------------------------------------------------------ */

  const isScalar = (v) => v === null || ['string', 'number', 'boolean'].includes(typeof v);
  const isNumeric = (v) => typeof v === 'number';

  /**
   * Describe the shape of a metric value so the report can pick a render.
   * Types: empty | scalar | range | vector | matrix | table | record | json
   */
  function describeValue(v) {
    if (v === undefined || v === null) return { type: 'empty' };
    if (isScalar(v)) return { type: 'scalar' };
    if (Array.isArray(v)) {
      if (v.length === 0) return { type: 'empty' };
      if (v.every(isScalar)) {
        const numeric = v.every(isNumeric);
        if (numeric && v.length === 2) return { type: 'range', numeric };
        return { type: 'vector', numeric, plottable: numeric && v.length > 2 };
      }
      if (v.every((row) => Array.isArray(row) && row.every(isScalar))) {
        return { type: 'matrix', rows: v.length, cols: Math.max(...v.map((r) => r.length)) };
      }
      return { type: 'json' };
    }
    const keys = Object.keys(v);
    if (keys.length === 0) return { type: 'empty' };
    if (keys.every((k) => Array.isArray(v[k]) && v[k].every(isScalar))) {
      const columns = keys.map((name) => {
        const values = v[name];
        return {
          name,
          length: values.length,
          numeric: values.length > 0 && values.every((x) => isNumeric(x) || x === null),
          monotonic: isMonotonic(values),
          distinct: new Set(values).size,
        };
      });
      const rows = Math.max(...columns.map((c) => c.length));
      const equalLengths = columns.every((c) => c.length === rows);
      const numericColumns = columns.filter((c) => c.numeric && c.length === rows);
      const plottable = equalLengths && rows > 1 && numericColumns.length >= 2;
      let plot = null;
      if (plottable) {
        // Prefer a monotonic column as x (e.g. retention time); then a line
        // plot reads naturally, otherwise fall back to a scatter plot.
        // As y prefer the column with the most distinct values (e.g. intensity
        // over a charge state column).
        const x = numericColumns.find((c) => c.monotonic) || numericColumns[0];
        const y = numericColumns.filter((c) => c !== x)
          .reduce((best, c) => (c.distinct > best.distinct ? c : best));
        plot = { x: x.name, y: y.name, mode: x.monotonic ? 'line' : 'scatter' };
      }
      return { type: 'table', columns, rows, equalLengths, plottable, plot };
    }
    if (keys.every((k) => isScalar(v[k]))) return { type: 'record' };
    return { type: 'json' };
  }

  function isMonotonic(values) {
    if (values.length < 2 || !values.every(isNumeric)) return false;
    let up = true;
    let down = true;
    for (let k = 1; k < values.length; k++) {
      if (values[k] < values[k - 1]) up = false;
      if (values[k] > values[k - 1]) down = false;
    }
    return up || down;
  }

  /** Human readable unit text; units may be one CV term or a list of terms. */
  function unitText(unit) {
    if (!unit) return '';
    const terms = Array.isArray(unit) ? unit : [unit];
    return terms.map((t) => (t && (t.name || t.accession)) || '').filter(Boolean).join(', ');
  }

  /**
   * Build the report model from the plain document. Paths are JSON-pointer
   * style ("/mzQC/runQualities/0/qualityMetrics/2") and match the source view.
   */
  function buildReport(doc) {
    const warnings = [];
    let mzqc = doc;
    let base = '';
    if (doc && typeof doc === 'object' && !Array.isArray(doc) && 'mzQC' in doc) {
      mzqc = doc.mzQC;
      base = '/mzQC';
    } else {
      warnings.push('No top level "mzQC" element; showing the document as is.');
    }
    if (!mzqc || typeof mzqc !== 'object' || Array.isArray(mzqc)) {
      return { ok: false, warnings: warnings.concat('The document is not an mzQC object.') };
    }

    const qualities = [];
    for (const [listKey, kind] of [['runQualities', 'run'], ['setQualities', 'set']]) {
      const list = Array.isArray(mzqc[listKey]) ? mzqc[listKey] : [];
      list.forEach((q, index) => {
        const path = `${base}/${listKey}/${index}`;
        const metadata = (q && q.metadata) || {};
        const metrics = (Array.isArray(q && q.qualityMetrics) ? q.qualityMetrics : []).map((m, k) => ({
          path: `${path}/qualityMetrics/${k}`,
          accession: m.accession || '',
          name: m.name || m.accession || `metric ${k + 1}`,
          description: m.description || '',
          unit: unitText(m.unit),
          value: m.value,
          shape: describeValue(m.value),
        }));
        qualities.push({
          kind,
          index,
          path,
          label: metadata.label || `${kind} ${index + 1}`,
          inputFiles: Array.isArray(metadata.inputFiles) ? metadata.inputFiles : [],
          analysisSoftware: Array.isArray(metadata.analysisSoftware) ? metadata.analysisSoftware : [],
          cvParameters: Array.isArray(metadata.cvParameters) ? metadata.cvParameters : [],
          metrics,
        });
      });
    }
    if (qualities.length === 0) warnings.push('The file contains no runQualities or setQualities.');

    return {
      ok: true,
      warnings,
      meta: {
        version: mzqc.version,
        creationDate: mzqc.creationDate,
        contactName: mzqc.contactName,
        contactAddress: mzqc.contactAddress,
        description: mzqc.description,
      },
      controlledVocabularies: Array.isArray(mzqc.controlledVocabularies) ? mzqc.controlledVocabularies : [],
      qualities,
      metricCount: qualities.reduce((sum, q) => sum + q.metrics.length, 0),
    };
  }

  /* ------------------------------------------------------------------ */
  /* Formatting helpers shared with the view                            */
  /* ------------------------------------------------------------------ */

  /** Compact number text: integers as is, floats to 6 significant digits. */
  function formatNumber(v) {
    if (typeof v !== 'number') return String(v);
    if (!Number.isFinite(v)) return String(v);
    if (Number.isInteger(v)) return String(v);
    const abs = Math.abs(v);
    if (abs !== 0 && (abs < 1e-4 || abs >= 1e9)) return v.toExponential(4);
    return String(Number(v.toPrecision(6)));
  }

  /** Short axis tick text: exponent notation for very large/small values. */
  function formatTick(v) {
    const abs = Math.abs(v);
    if (abs !== 0 && (abs >= 1e5 || abs < 1e-3)) {
      const [mant, exp] = v.toExponential().split('e');
      return `${Number(Number(mant).toPrecision(3))}e${Number(exp)}`;
    }
    return formatNumber(v);
  }

  /** Axis ticks at 1/2/5 x 10^k steps covering [min, max]. */
  function niceTicks(min, max, target = 5) {
    if (!Number.isFinite(min) || !Number.isFinite(max)) return [];
    if (min === max) {
      const d = min === 0 ? 1 : Math.abs(min) * 0.1;
      min -= d;
      max += d;
    }
    const raw = (max - min) / Math.max(1, target);
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const norm = raw / mag;
    const step = (norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10) * mag;
    const first = Math.ceil(min / step - 1e-9) * step;
    const ticks = [];
    for (let t = first; t <= max + step * 1e-9; t += step) {
      // round away floating point noise such as 0.30000000000000004
      ticks.push(Number(t.toPrecision(12)));
    }
    return ticks;
  }

  return {
    ParseError,
    parse,
    readability2,
    serialize,
    toPlain,
    keyClass,
    valueClass,
    describeValue,
    unitText,
    buildReport,
    formatNumber,
    formatTick,
    niceTicks,
    MZQC_KEYS,
  };
});
