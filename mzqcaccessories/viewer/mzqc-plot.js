/*
 * mzqc-plot.js — small dependency-free SVG line/scatter plots for the report.
 * Requires mzqc-core.js (tick and number formatting). Exposes `MzqcPlot`.
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
   *          mode: 'line'|'scatter', width?: number, height?: number}} spec
   * @returns {SVGSVGElement}
   */
  function render(container, spec) {
    const width = spec.width || 640;
    const height = spec.height || 280;
    const m = { top: 12, right: 16, bottom: 44, left: 64 };
    const pw = width - m.left - m.right;
    const ph = height - m.top - m.bottom;

    const points = [];
    for (let k = 0; k < Math.min(spec.x.length, spec.y.length); k++) {
      const px = spec.x[k];
      const py = spec.y[k];
      if (Number.isFinite(px) && Number.isFinite(py)) points.push([px, py]);
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

    overlay.addEventListener('pointermove', (ev) => {
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
    return svg;
  }

  root.MzqcPlot = { render };
})(typeof self !== 'undefined' ? self : this);
