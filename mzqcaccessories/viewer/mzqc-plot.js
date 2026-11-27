/*
 * mzqc-plot.js — small dependency-free plots for the report: SVG line/scatter
 * plots and canvas heatmaps for matrices. Requires mzqc-core.js (tick and
 * number formatting). Exposes `MzqcPlot`.
 */
(function (root) {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const Core = root.MzqcCore;

  function el(name, attrs, parent) {
    const node = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  }

  /**
   * Draw a plot into `container` (replacing its content).
   * @param {HTMLElement} container
   * @param {{x: number[], y: number[], xLabel: string, yLabel: string,
   *          mode: 'line'|'scatter', width?: number, height?: number,
   *          onPick?: function(number)}} spec  `onPick` gets the index (into x and y)
   *          of the point nearest to a click
   * @returns {SVGSVGElement}
   */
  function render(container, spec) {
    const width = spec.width || 640;
    const height = spec.height || 280;
    const m = { top: 12, right: 16, bottom: 44, left: 64 };
    const pw = width - m.left - m.right;
    const ph = height - m.top - m.bottom;

    const points = []; // [x, y, index into spec.x and spec.y]
    for (let k = 0; k < Math.min(spec.x.length, spec.y.length); k++) {
      const px = spec.x[k];
      const py = spec.y[k];
      if (Number.isFinite(px) && Number.isFinite(py)) points.push([px, py, k]);
    }

    container.textContent = '';
    const svg = el('svg', {
      class: 'plot',
      viewBox: `0 0 ${width} ${height}`,
      role: 'img',
      'aria-label': `${spec.mode} plot of ${spec.yLabel} against ${spec.xLabel}, ${points.length} points`,
    }, container);

    if (points.length === 0) {
      el('text', { x: width / 2, y: height / 2, class: 'plot-empty', 'text-anchor': 'middle' }, svg)
        .textContent = 'No finite values to plot';
      return svg;
    }

    let [xmin, xmax, ymin, ymax] = [Infinity, -Infinity, Infinity, -Infinity];
    for (const [px, py] of points) {
      if (px < xmin) xmin = px;
      if (px > xmax) xmax = px;
      if (py < ymin) ymin = py;
      if (py > ymax) ymax = py;
    }
    const xticks = Core.niceTicks(xmin, xmax, 6);
    const yticks = Core.niceTicks(ymin, ymax, 5);
    const x0 = Math.min(xmin, xticks[0]);
    const x1 = Math.max(xmax, xticks[xticks.length - 1]);
    const y0 = Math.min(ymin, yticks[0]);
    const y1 = Math.max(ymax, yticks[yticks.length - 1]);
    const sx = (v) => m.left + (x1 === x0 ? pw / 2 : ((v - x0) / (x1 - x0)) * pw);
    const sy = (v) => m.top + ph - (y1 === y0 ? ph / 2 : ((v - y0) / (y1 - y0)) * ph);

    const grid = el('g', { class: 'plot-grid' }, svg);
    const axes = el('g', { class: 'plot-axis' }, svg);
    for (const t of yticks) {
      const y = sy(t);
      el('line', { x1: m.left, x2: m.left + pw, y1: y, y2: y }, grid);
      el('text', { x: m.left - 6, y: y + 4, 'text-anchor': 'end' }, axes).textContent = Core.formatTick(t);
    }
    for (const t of xticks) {
      const x = sx(t);
      el('line', { x1: x, x2: x, y1: m.top, y2: m.top + ph }, grid);
      el('text', { x, y: m.top + ph + 16, 'text-anchor': 'middle' }, axes).textContent = Core.formatTick(t);
    }
    el('line', { x1: m.left, x2: m.left + pw, y1: m.top + ph, y2: m.top + ph, class: 'plot-baseline' }, axes);
    el('line', { x1: m.left, x2: m.left, y1: m.top, y2: m.top + ph, class: 'plot-baseline' }, axes);
    el('text', { x: m.left + pw / 2, y: height - 6, 'text-anchor': 'middle', class: 'plot-label' }, axes)
      .textContent = spec.xLabel;
    el('text', {
      x: 0, y: 0, 'text-anchor': 'middle', class: 'plot-label',
      transform: `translate(14 ${m.top + ph / 2}) rotate(-90)`,
    }, axes).textContent = spec.yLabel;

    const pixels = points.map(([px, py]) => [sx(px), sy(py)]);
    const d = [];
    if (spec.mode === 'line') {
      pixels.forEach(([px, py], k) => d.push(`${k ? 'L' : 'M'}${px.toFixed(1)} ${py.toFixed(1)}`));
      el('path', { d: d.join(''), class: 'plot-line' }, svg);
    } else {
      // One path of zero-length round-capped segments draws all dots cheaply.
      pixels.forEach(([px, py]) => d.push(`M${px.toFixed(1)} ${py.toFixed(1)}h0`));
      el('path', { d: d.join(''), class: 'plot-dots' }, svg);
    }

    // Hover read-out of the nearest point.
    const marker = el('circle', { r: 4.5, class: 'plot-marker', visibility: 'hidden' }, svg);
    const tip = el('g', { class: 'plot-tip', visibility: 'hidden' }, svg);
    const tipBox = el('rect', { rx: 4, height: 22 }, tip);
    const tipText = el('text', { y: 15 }, tip);
    const overlay = el('rect', {
      x: m.left, y: m.top, width: pw, height: ph, class: 'plot-overlay',
    }, svg);

    // A line plot reads along x, so there the nearest point is the nearest in x.
    function nearest(ev) {
      const box = svg.getBoundingClientRect();
      const mx = ((ev.clientX - box.left) / box.width) * width;
      const my = ((ev.clientY - box.top) / box.height) * height;
      let best = 0;
      let bestDist = Infinity;
      for (let k = 0; k < pixels.length; k++) {
        const dx = pixels[k][0] - mx;
        const dy = spec.mode === 'line' ? 0 : pixels[k][1] - my;
        const dist = dx * dx + dy * dy;
        if (dist < bestDist) { bestDist = dist; best = k; }
      }
      return best;
    }

    overlay.addEventListener('pointermove', (ev) => {
      const best = nearest(ev);
      const [px, py] = pixels[best];
      marker.setAttribute('cx', px);
      marker.setAttribute('cy', py);
      marker.setAttribute('visibility', 'visible');
      tipText.textContent = `${spec.xLabel}: ${Core.formatNumber(points[best][0])}  ${spec.yLabel}: ${Core.formatNumber(points[best][1])}`;
      const tw = tipText.getComputedTextLength() + 16;
      const tx = Math.min(Math.max(px - tw / 2, m.left), m.left + pw - tw);
      const ty = py - 32 < m.top ? py + 10 : py - 32;
      tipBox.setAttribute('width', tw);
      tipText.setAttribute('x', 8);
      tip.setAttribute('transform', `translate(${tx} ${ty})`);
      tip.setAttribute('visibility', 'visible');
    });
    overlay.addEventListener('pointerleave', () => {
      marker.setAttribute('visibility', 'hidden');
      tip.setAttribute('visibility', 'hidden');
    });
    if (spec.onPick) overlay.addEventListener('click', (ev) => spec.onPick(points[nearest(ev)][2]));
    return svg;
  }

  /* ------------------------------------------------------------------ */
  /* Heatmaps                                                           */
  /* ------------------------------------------------------------------ */

  // Display size limits of a heatmap, in CSS pixels.
  const HEAT_MAX_WIDTH = 760;
  const HEAT_MAX_HEIGHT = 520;
  const HEAT_MAX_CELL = 24;
  // Only used if the stylesheet with the --heat-* ramps is missing.
  const FALLBACK_RAMP = ['#e0e0e0', '#303030'];

  function div(cls, ...children) {
    const node = document.createElement('div');
    if (cls) node.className = cls;
    node.append(...children);
    return node;
  }

  /** Colour stops of a CSS custom property holding a comma separated hex list. */
  function rampStops(property) {
    const stops = getComputedStyle(document.documentElement).getPropertyValue(property)
      .split(',').map((s) => s.trim()).filter((s) => /^#[0-9a-f]{6}$/i.test(s));
    return stops.length >= 2 ? stops : FALLBACK_RAMP;
  }

  /**
   * RGB lookup table of 257 colours evenly interpolated along the stops, the
   * way a CSS linear-gradient of the same stops is drawn. 257 (not 256)
   * entries put the centre of a diverging ramp exactly on entry 128.
   */
  function lookupTable(stops) {
    const rgb = stops.map((s) => [1, 3, 5].map((k) => parseInt(s.slice(k, k + 2), 16)));
    const lut = new Uint8ClampedArray(257 * 3);
    for (let k = 0; k <= 256; k++) {
      const pos = (k / 256) * (rgb.length - 1);
      const i = Math.min(rgb.length - 2, Math.floor(pos));
      for (let ch = 0; ch < 3; ch++) lut[k * 3 + ch] = rgb[i][ch] + (rgb[i + 1][ch] - rgb[i][ch]) * (pos - i);
    }
    return lut;
  }

  function scaleLegend(scale, label, hasMissing) {
    const bar = div('heat-bar');
    const ticks = div('heat-ticks');
    const span = scale.hi - scale.lo;
    for (const t of span > 0 ? Core.niceTicks(scale.lo, scale.hi, 4) : [scale.lo]) {
      const pos = span > 0 ? (t - scale.lo) / span : 0.5;
      const tick = document.createElement('span');
      tick.textContent = Core.formatTick(t);
      tick.style.left = `${pos * 100}%`;
      // Labels near the ends align to the bar's edge instead of overhanging it.
      tick.style.transform = `translateX(${pos < 0.1 ? 0 : pos > 0.9 ? -100 : -50}%)`;
      ticks.append(tick);
    }
    const notes = div('heat-notes');
    if (hasMissing) notes.append(div(null, div('heat-swatch'), 'no value'));
    if (scale.clipped) {
      notes.append(div(null, `Colours span the 1st–99th percentile; all values: ${Core.formatNumber(scale.min)} – ${Core.formatNumber(scale.max)}`));
    }
    return { legend: div('heat-legend', div('heat-scale', bar, ticks, div('heat-label', label)), notes), bar };
  }

  /**
   * Draw a numeric matrix as a heatmap with a colour scale into `container`
   * (replacing its content). Row 0 is at the top, as in the table view.
   * Values beyond the scale take its end colours; null and non-finite cells
   * stay transparent ("no value"). Hovering or focusing a cell shows its value.
   * @param {HTMLElement} container
   * @param {{matrix: Array<Array<number|null>>, rows: number, cols: number,
   *          scale: object, label?: string, onPick?: function(number, number)}} spec
   *          `scale` from MzqcCore.heatScale(); `onPick` gets the row and column of a
   *          clicked cell, or of the focused cell on Enter
   * @returns {HTMLElement} the heatmap element
   */
  function heatmap(container, spec) {
    const { matrix, rows, cols, scale } = spec;
    const label = spec.label || 'value';
    // Square cells, as large as fit the limits; a long, thin matrix gets
    // elongated cells so that it does not shrink to a line.
    const cell = Math.min(HEAT_MAX_CELL, HEAT_MAX_WIDTH / cols, HEAT_MAX_HEIGHT / rows);
    const width = Math.max(cols * cell, Math.min(cols * HEAT_MAX_CELL, 48));
    const height = Math.max(rows * cell, Math.min(rows * HEAT_MAX_CELL, 48));

    const canvas = document.createElement('canvas');
    canvas.width = cols;
    canvas.height = rows;
    canvas.tabIndex = 0;
    canvas.setAttribute('role', 'img');
    canvas.setAttribute('aria-label', `Heatmap of ${rows} × ${cols} cells, colour shows ${label} from ` +
      `${Core.formatNumber(scale.lo)} to ${Core.formatNumber(scale.hi)}; arrow keys read single cells` +
      (spec.onPick ? ', Enter selects one' : ''));
    const cursor = div('heatmap-cursor');
    const tipValue = document.createElement('strong');
    const tipWhere = div('heatmap-where');
    const tip = div('heatmap-tip', tipValue, tipWhere);
    cursor.hidden = true;
    tip.hidden = true;
    const frame = div('heatmap-frame', canvas, cursor);
    frame.style.maxWidth = `${width}px`;
    frame.style.aspectRatio = `${width} / ${height}`;
    const { legend, bar } = scaleLegend(scale, label, scale.missing > 0);
    const block = div('heatmap', frame, legend, tip);

    block._paint = () => {
      const stops = rampStops(scale.diverging ? '--heat-div' : '--heat-seq');
      const lut = lookupTable(stops);
      const ctx = canvas.getContext('2d');
      const image = ctx.createImageData(cols, rows);
      const px = image.data;
      const span = scale.hi - scale.lo;
      for (let r = 0; r < rows; r++) {
        const row = matrix[r];
        for (let c = 0; c < row.length; c++) {
          const v = row[c];
          if (!Number.isFinite(v)) continue;
          const t = span > 0 ? Math.min(1, Math.max(0, (v - scale.lo) / span)) : 0.5;
          const k = Math.round(t * 256) * 3;
          const o = (r * cols + c) * 4;
          px[o] = lut[k];
          px[o + 1] = lut[k + 1];
          px[o + 2] = lut[k + 2];
          px[o + 3] = 255;
        }
      }
      ctx.putImageData(image, 0, 0);
      bar.style.background = `linear-gradient(to right, ${stops.join(', ')})`;
    };
    block._paint();

    let active = null; // [row, column] shown in the tooltip
    function show(r, c, clientX, clientY) {
      active = [r, c];
      const v = matrix[r][c];
      tipValue.textContent = typeof v === 'number' ? `${Core.formatNumber(v)} ${spec.label || ''}`.trim() : 'no value';
      tipWhere.textContent = `row ${r}, column ${c}`;
      cursor.style.left = `${((c + 0.5) / cols) * 100}%`;
      cursor.style.top = `${((r + 0.5) / rows) * 100}%`;
      cursor.style.width = `max(6px, ${100 / cols}%)`;
      cursor.style.height = `max(6px, ${100 / rows}%)`;
      cursor.hidden = false;
      tip.hidden = false;
      // Fixed position next to the point, flipped to stay inside the window.
      let x = clientX + 14;
      let y = clientY + 14;
      if (x + tip.offsetWidth > window.innerWidth - 4) x = clientX - 14 - tip.offsetWidth;
      if (y + tip.offsetHeight > window.innerHeight - 4) y = clientY - 14 - tip.offsetHeight;
      tip.style.left = `${Math.max(4, x)}px`;
      tip.style.top = `${Math.max(4, y)}px`;
    }
    function showCell(r, c) {
      const box = canvas.getBoundingClientRect();
      show(r, c, box.left + ((c + 1) / cols) * box.width, box.top + ((r + 1) / rows) * box.height);
    }
    function hide() {
      cursor.hidden = true;
      tip.hidden = true;
    }
    const clamp = (v, max) => Math.min(max, Math.max(0, v));
    function cellAt(ev) {
      const box = canvas.getBoundingClientRect();
      return [clamp(Math.floor(((ev.clientY - box.top) / box.height) * rows), rows - 1),
        clamp(Math.floor(((ev.clientX - box.left) / box.width) * cols), cols - 1)];
    }

    canvas.addEventListener('pointermove', (ev) => show(...cellAt(ev), ev.clientX, ev.clientY));
    canvas.addEventListener('pointerleave', hide);
    if (spec.onPick) canvas.addEventListener('click', (ev) => spec.onPick(...cellAt(ev)));
    canvas.addEventListener('focus', () => showCell(...(active || [0, 0])));
    canvas.addEventListener('blur', hide);
    canvas.addEventListener('keydown', (ev) => {
      if (ev.key === 'Enter' && spec.onPick) {
        spec.onPick(...(active || [0, 0]));
        return;
      }
      const step = ev.shiftKey ? 10 : 1;
      const move = { ArrowUp: [-step, 0], ArrowDown: [step, 0], ArrowLeft: [0, -step], ArrowRight: [0, step] }[ev.key];
      if (!move) return;
      ev.preventDefault();
      const [r, c] = active || [0, 0];
      showCell(clamp(r + move[0], rows - 1), clamp(c + move[1], cols - 1));
    });

    container.textContent = '';
    container.append(block);
    return block;
  }

  // Canvas pixels and legend gradients take the --heat-* colours when drawn;
  // redraw them when the colour scheme switches between light and dark.
  if (root.matchMedia) {
    root.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      document.querySelectorAll('.heatmap').forEach((node) => node._paint && node._paint());
    });
  }

  root.MzqcPlot = { render, heatmap };
})(typeof self !== 'undefined' ? self : this);
