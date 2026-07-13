/* canvas-fx.js — academic-deck-animator 自寫粒子引擎
 * 三種學術場合允許的低調特效。API:
 *   const fx = CanvasFX.mount(canvasEl, 'particle-burst', { intensity:'low', colors:['#38BDF8','#F59E0B'] });
 *   fx.stop();  // 離開該頁時呼叫
 * 所有特效尊重 prefers-reduced-motion:使用者系統設定減少動態時自動降為靜態。
 */
(function (global) {
  'use strict';

  var INTENSITY = { low: 0.5, medium: 1.0, high: 1.8 };
  var reduced = global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function rand(a, b) { return a + Math.random() * (b - a); }

  function makeCtx(canvas) {
    var dpr = global.devicePixelRatio || 1;
    var w = canvas.clientWidth, h = canvas.clientHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return { ctx: ctx, w: w, h: h };
  }

  /* --- particle-burst:從中心偏下爆發、緩慢上飄消散;開場一次+低速餘燼 --- */
  function particleBurst(canvas, opts) {
    var s = makeCtx(canvas), k = INTENSITY[opts.intensity] || 0.5;
    var N = Math.round(90 * k), parts = [], t0 = null, raf = null;
    for (var i = 0; i < N; i++) {
      var ang = rand(0, Math.PI * 2), sp = rand(0.4, 2.6) * k;
      parts.push({
        x: s.w / 2, y: s.h * 0.62,
        vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp - 0.6 * k,
        r: rand(0.8, 2.6), life: rand(2.5, 6),
        c: opts.colors[i % opts.colors.length]
      });
    }
    function frame(ts) {
      if (!t0) t0 = ts;
      var dt = 1 / 60;
      s.ctx.clearRect(0, 0, s.w, s.h);
      parts.forEach(function (p) {
        p.x += p.vx; p.y += p.vy;
        p.vy -= 0.002; p.vx *= 0.998; p.life -= dt;
        if (p.life <= 0 || p.y < -10) { // 回收為緩慢餘燼
          p.x = rand(0, s.w); p.y = s.h + 5;
          p.vx = rand(-0.15, 0.15); p.vy = rand(-0.5, -0.2) * k;
          p.life = rand(4, 9); p.r = rand(0.5, 1.6);
        }
        s.ctx.globalAlpha = Math.max(0, Math.min(1, p.life / 3)) * 0.75;
        s.ctx.fillStyle = p.c;
        s.ctx.beginPath(); s.ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); s.ctx.fill();
      });
      s.ctx.globalAlpha = 1;
      raf = global.requestAnimationFrame(frame);
    }
    if (reduced) { staticDots(s, parts.slice(0, 30)); return { stop: function () {} }; }
    raf = global.requestAnimationFrame(frame);
    return { stop: function () { global.cancelAnimationFrame(raf); } };
  }

  /* --- drift-field:全畫面緩慢漂浮微粒,近乎靜止的沉穩背景 --- */
  function driftField(canvas, opts) {
    var s = makeCtx(canvas), k = INTENSITY[opts.intensity] || 0.5;
    var N = Math.round(45 * k), parts = [], raf = null;
    for (var i = 0; i < N; i++) {
      parts.push({
        x: rand(0, s.w), y: rand(0, s.h),
        vx: rand(-0.12, 0.12) * k, vy: rand(-0.08, 0.08) * k,
        r: rand(0.6, 2.2), a: rand(0.12, 0.4),
        c: opts.colors[i % opts.colors.length]
      });
    }
    function frame() {
      s.ctx.clearRect(0, 0, s.w, s.h);
      parts.forEach(function (p) {
        p.x = (p.x + p.vx + s.w) % s.w; p.y = (p.y + p.vy + s.h) % s.h;
        s.ctx.globalAlpha = p.a; s.ctx.fillStyle = p.c;
        s.ctx.beginPath(); s.ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); s.ctx.fill();
      });
      s.ctx.globalAlpha = 1;
      raf = global.requestAnimationFrame(frame);
    }
    if (reduced) { staticDots(s, parts); return { stop: function () {} }; }
    raf = global.requestAnimationFrame(frame);
    return { stop: function () { global.cancelAnimationFrame(raf); } };
  }

  /* --- network-lines:漂移節點+距離連線,適合「網絡/連結」主題 --- */
  function networkLines(canvas, opts) {
    var s = makeCtx(canvas), k = INTENSITY[opts.intensity] || 0.5;
    var N = Math.round(26 * k), R = 130, nodes = [], raf = null;
    for (var i = 0; i < N; i++) {
      nodes.push({ x: rand(0, s.w), y: rand(0, s.h),
        vx: rand(-0.25, 0.25) * k, vy: rand(-0.25, 0.25) * k });
    }
    function frame() {
      s.ctx.clearRect(0, 0, s.w, s.h);
      nodes.forEach(function (n) {
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > s.w) n.vx *= -1;
        if (n.y < 0 || n.y > s.h) n.vy *= -1;
      });
      for (var i = 0; i < N; i++) {
        for (var j = i + 1; j < N; j++) {
          var dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y;
          var d = Math.sqrt(dx * dx + dy * dy);
          if (d < R) {
            s.ctx.globalAlpha = (1 - d / R) * 0.35;
            s.ctx.strokeStyle = opts.colors[0];
            s.ctx.lineWidth = 0.6;
            s.ctx.beginPath();
            s.ctx.moveTo(nodes[i].x, nodes[i].y);
            s.ctx.lineTo(nodes[j].x, nodes[j].y);
            s.ctx.stroke();
          }
        }
      }
      s.ctx.globalAlpha = 0.7; s.ctx.fillStyle = opts.colors[0];
      nodes.forEach(function (n) {
        s.ctx.beginPath(); s.ctx.arc(n.x, n.y, 1.8, 0, Math.PI * 2); s.ctx.fill();
      });
      s.ctx.globalAlpha = 1;
      raf = global.requestAnimationFrame(frame);
    }
    if (reduced) { staticDots(s, nodes.map(function (n) { return { x: n.x, y: n.y, r: 1.8, a: 0.5, c: opts.colors[0] }; })); return { stop: function () {} }; }
    raf = global.requestAnimationFrame(frame);
    return { stop: function () { global.cancelAnimationFrame(raf); } };
  }

  function staticDots(s, parts) { // reduced-motion 退化:畫一次靜態微粒
    parts.forEach(function (p) {
      s.ctx.globalAlpha = p.a || 0.3; s.ctx.fillStyle = p.c || '#888';
      s.ctx.beginPath(); s.ctx.arc(p.x, p.y, p.r || 1.5, 0, Math.PI * 2); s.ctx.fill();
    });
    s.ctx.globalAlpha = 1;
  }

  var REGISTRY = {
    'particle-burst': particleBurst,
    'drift-field': driftField,
    'network-lines': networkLines
  };

  global.CanvasFX = {
    mount: function (canvas, fxName, opts) {
      var fn = REGISTRY[fxName];
      if (!fn || !canvas) return { stop: function () {} };
      opts = opts || {};
      opts.intensity = opts.intensity || 'low';
      opts.colors = (opts.colors && opts.colors.length) ? opts.colors : ['#38BDF8', '#F59E0B'];
      return fn(canvas, opts);
    }
  };
})(window);
