/* Unit tests for mzqc-core.js; run by tests/index.html. */
/* global test, eq, assert, throws, MzqcCore */
(function () {
  'use strict';
  const C = MzqcCore;
  const roundTrip = (text) => C.serialize(C.parse(text).root);

  test('parse keeps the source text of numbers', () => {
    const { root } = C.parse('{"a": 1.0, "b": 1e3, "c": -0.50}');
    eq(root.entries.map((e) => e.value.raw), ['1.0', '1e3', '-0.50']);
    eq(root.entries.map((e) => e.value.value), [1, 1000, -0.5]);
  });

  test('parse handles all scalar kinds and escapes', () => {
    const plain = C.toPlain(C.parse('{"s": "a\\"b\\u00e9\\n", "t": true, "f": false, "n": null, "arr": [], "obj": {}}').root);
    eq(plain, { s: 'a"bé\n', t: true, f: false, n: null, arr: [], obj: {} });
  });

  test('parse accepts a byte order mark', () => {
    eq(C.toPlain(C.parse('﻿{"a": 1}').root), { a: 1 });
  });

  test('parse reports line and column of errors', () => {
    const err = throws(() => C.parse('{\n  "a": 1,\n  "b": ]\n}'), /Unexpected character/);
    eq([err.line, err.column], [3, 8]);
  });

  test('parse rejects trailing commas and trailing content', () => {
    throws(() => C.parse('[1, 2,]'));
    throws(() => C.parse('{"a": 1} x'), /after the JSON document/);
    throws(() => C.parse('{"a": 1'), /Unclosed object/);
  });

  test('parse accepts Python NaN/Infinity with warnings', () => {
    const { root, warnings } = C.parse('[NaN, Infinity, -Infinity]');
    eq(root.items.map((n) => n.raw), ['NaN', 'Infinity', '-Infinity']);
    assert(Number.isNaN(root.items[0].value));
    eq(warnings.length, 3);
  });

  test('parse warns about duplicate keys', () => {
    const { warnings } = C.parse('{"a": 1, "a": 2}');
    assert(/Duplicate key "a"/.test(warnings[0]), warnings[0]);
  });

  test('serialize matches Python json.dumps(indent=4) layout', () => {
    eq(roundTrip('{"a":[1,2.50,{"b":null}],"c":{},"d":[],"e":"x"}'),
      '{\n    "a": [\n        1,\n        2.50,\n        {\n            "b": null\n        }\n    ],\n' +
      '    "c": {},\n    "d": [],\n    "e": "x"\n}');
  });

  test('readability2 drops empty optional elements only', () => {
    const tree = C.readability2(C.parse(JSON.stringify({
      mzQC: {
        version: '1.0.0', contactName: '', contactAddress: '', description: '',
        runQualities: [{ metadata: { label: 'x', cvParameters: [], inputFiles: [{ name: 'f', fileProperties: [] }] },
          qualityMetrics: [{ accession: 'MS:1', name: 'm', value: '', description: '' }] }],
        setQualities: [],
      },
    })).root);
    eq(C.toPlain(tree), {
      mzQC: {
        version: '1.0.0',
        runQualities: [{ metadata: { label: 'x', inputFiles: [{ name: 'f' }] },
          qualityMetrics: [{ accession: 'MS:1', name: 'm', value: '' }] }],
      },
    });
  });

  test('readability2 keeps non-empty optional elements', () => {
    const src = '{"description": "d", "fileProperties": [1], "contactName": "n"}';
    eq(C.toPlain(C.readability2(C.parse(src).root)), JSON.parse(src));
  });

  test('keyClass separates schema keys from data keys', () => {
    eq(C.keyClass('qualityMetrics', false), 'key-mzqc');
    eq(C.keyClass('retention time', false), 'key-data');
    eq(C.keyClass('name', true), 'key-data');
  });

  test('valueClass colours by type and role', () => {
    const s = (v) => ({ kind: 'string', value: v });
    eq(C.valueClass(s('MS:4000059'), 'accession'), 'accession');
    eq(C.valueClass(s('not an accession'), 'accession'), 'string');
    eq(C.valueClass(s('https://x'), 'uri'), 'uri');
    eq(C.valueClass(s('2020-01-01'), 'creationDate'), 'date');
    eq(C.valueClass({ kind: 'number', raw: '1', value: 1 }, 'value'), 'number');
    eq(C.valueClass({ kind: 'boolean', value: true }), 'boolean');
    eq(C.valueClass({ kind: 'null', value: null }), 'null');
  });

  test('describeValue recognises value shapes', () => {
    eq(C.describeValue(5).type, 'scalar');
    eq(C.describeValue('x').type, 'scalar');
    eq(C.describeValue(null).type, 'empty');
    eq(C.describeValue([]).type, 'empty');
    eq(C.describeValue([1, 2]).type, 'range');
    eq(C.describeValue([1, 2, 3]), { type: 'vector', numeric: true, plottable: true });
    eq(C.describeValue(['a', 'b', 'c']), { type: 'vector', numeric: false, plottable: false });
    eq(C.describeValue([[1, 2], [3, 4]]).type, 'matrix');
    eq(C.describeValue({ a: 1, b: 'x' }).type, 'record');
    eq(C.describeValue({ a: { b: 1 } }).type, 'json');
  });

  test('describeValue picks a monotonic x column and line plot for tables', () => {
    const shape = C.describeValue({ intensity: [5, 1, 3], rt: [1, 2, 3], label: ['a', 'b', 'c'] });
    eq(shape.type, 'table');
    eq(shape.rows, 3);
    assert(shape.plottable);
    eq(shape.plot, { x: 'rt', y: 'intensity', mode: 'line' });
  });

  test('describeValue uses scatter when no column is monotonic', () => {
    eq(C.describeValue({ a: [3, 1, 2], b: [1, 3, 2] }).plot.mode, 'scatter');
  });

  test('describeValue does not plot ragged or single-numeric tables', () => {
    assert(!C.describeValue({ a: [1, 2, 3], b: [1, 2] }).plottable);
    assert(!C.describeValue({ a: [1, 2, 3], b: ['x', 'y', 'z'] }).plottable);
  });

  test('unitText handles single and per-column units', () => {
    eq(C.unitText({ accession: 'UO:0000189', name: 'count unit' }), 'count unit');
    eq(C.unitText([{ name: 'second' }, { accession: 'MS:1' }]), 'second, MS:1');
    eq(C.unitText(undefined), '');
  });

  test('buildReport collects runs, sets and metrics with source paths', () => {
    const report = C.buildReport({
      mzQC: {
        version: '1.0.0',
        runQualities: [{ metadata: { label: 'r1' }, qualityMetrics: [{ accession: 'MS:1', name: 'a', value: 1 }] }],
        setQualities: [{ metadata: {}, qualityMetrics: [{ accession: 'MS:2', value: [1, 2, 3] }] }],
      },
    });
    assert(report.ok);
    eq(report.metricCount, 2);
    eq(report.qualities.map((q) => [q.kind, q.label, q.path]),
      [['run', 'r1', '/mzQC/runQualities/0'], ['set', 'set 1', '/mzQC/setQualities/0']]);
    eq(report.qualities[1].metrics[0].path, '/mzQC/setQualities/0/qualityMetrics/0');
    eq(report.qualities[1].metrics[0].name, 'MS:2');
  });

  test('buildReport warns about non-mzQC documents', () => {
    assert(!C.buildReport([1, 2]).ok);
    const r = C.buildReport({ foo: 1 });
    assert(r.warnings.some((w) => /No top level "mzQC"/.test(w)));
  });

  test('formatNumber is compact', () => {
    eq(C.formatNumber(5074), '5074');
    eq(C.formatNumber(300.157287597656), '300.157');
    eq(C.formatNumber(0.00001234), '1.2340e-5');
    eq(C.formatNumber(NaN), 'NaN');
  });

  test('describeValue prefers the most varied column as y', () => {
    eq(C.describeValue({ mz: [3, 1, 2, 5], charge: [2, 2, 3, 2], intensity: [9, 4, 7, 1] }).plot,
      { x: 'mz', y: 'intensity', mode: 'scatter' });
  });

  test('formatTick shortens large and small ticks', () => {
    eq(C.formatTick(15000000), '1.5e7');
    eq(C.formatTick(0.0002), '2e-4');
    eq(C.formatTick(2500), '2500');
    eq(C.formatTick(0), '0');
  });

  test('niceTicks uses 1/2/5 steps inside the range', () => {
    eq(C.niceTicks(0, 10, 5), [0, 2, 4, 6, 8, 10]);
    eq(C.niceTicks(0.1, 0.95, 4), [0.2, 0.4, 0.6, 0.8]);
    eq(C.niceTicks(300.16, 1778.86, 6), [400, 600, 800, 1000, 1200, 1400, 1600]);
    assert(C.niceTicks(5, 5).length > 0, 'constant range still gets ticks');
  });
})();
