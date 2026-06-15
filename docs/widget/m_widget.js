/* ============================================================
   m_widget — end-of-turn stats widget, denys.fast branded (obsidian/dark).
   Heavy design lives here (loaded once from jsDelivr + cached); the Stop hook
   only emits a tiny renderMWidget(<metrics>) call each turn, so no tokens are
   spent regenerating HTML.

   Pulls the real denys.fast wordmark (logo.css + logo.js) from the same repo
   via jsDelivr and renders it in the "obsidian" theme.

   Public API:  window.renderMWidget(metrics, mountId="mw")
   metrics = the hook's METRICS_JSON:
     { project, model, duration_human, cost_usd,
       tokens:{ new, input, output, cache_read, cache_write, total },
       tools_total, tools_by_name:{}, tool_failures, subagents_launched }
   ============================================================ */
(function (g) {
  "use strict";

  // Same-repo asset base. Bump the @vX.Y.Z tag together with the plugin release
  // so jsDelivr serves a stable, instantly-cached copy. Keep in sync with the
  // WIDGET_VER constant in hooks/turn_summary_widget.py.
  var BASE = g.MW_BASE || "https://cdn.jsdelivr.net/gh/mapuamap/denys-fast-mskills@v2.7.0/docs/";

  var INK = "#14171F", ACCENT = "#2DD4BF", TEXT = "#F4F4F5",
      DIM = "rgba(244,244,245,.55)", FAINT = "rgba(244,244,245,.32)",
      LINE = "rgba(244,244,245,.10)";

  function fmt(n) {
    n = Number(n) || 0;
    if (n >= 1e6) return (n / 1e6).toFixed(n >= 1e7 ? 0 : 1) + "M";
    if (n >= 1e3) return (n / 1e3).toFixed(n >= 1e4 ? 0 : 1) + "k";
    return String(Math.round(n));
  }
  function money(c) {
    c = Number(c) || 0;
    return "$" + (c < 0.01 ? c.toFixed(4) : c.toFixed(2));
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (m) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m];
    });
  }

  // minimalist binary (0/1) field — each cell cross-fades 0<->1 (pure CSS,
  // staggered timing per cell), built as an inline SVG. The "secondary mark"
  // sitting after the arrow next to the denys.fast wordmark.
  function buildBinary() {
    var cols = 7, rows = 3, cw = 9, ch = 12, W = cols * cw + 4, H = rows * ch + 2, s = "";
    for (var c = 0; c < cols; c++) {
      for (var r = 0; r < rows; r++) {
        var x = c * cw + 6, y = r * ch + 11;
        var dur = (1.5 + ((c * 7 + r * 13) % 9) * 0.21).toFixed(2);
        var del = (((c * 5 + r * 11) % 11) * 0.19).toFixed(2);
        var st = ' style="animation-duration:' + dur + 's;animation-delay:' + del + 's"';
        s += '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="b0"' + st + '>0</text>';
        s += '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="b1"' + st + '>1</text>';
      }
    }
    return '<svg class="mw-bits" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '" aria-hidden="true">' + s + '</svg>';
  }

  function injectStyle() {
    if (document.getElementById("mw-style")) return;
    var css =
      '@keyframes mw-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}' +
      '@keyframes mw-sweep{0%{background-position:-160% 0}100%{background-position:260% 0}}' +
      '@keyframes mw-b0{0%,46%{opacity:.78}54%,100%{opacity:0}}' +
      '@keyframes mw-b1{0%,46%{opacity:0}54%,100%{opacity:.78}}' +
      '.mw-card{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;width:100%;max-width:720px;box-sizing:border-box;' +
        'background:' + INK + ';border:0.5px solid ' + LINE + ';border-radius:14px;' +
        'padding:14px 20px 12px;color:' + TEXT + ';animation:mw-in .45s ease both;position:relative;overflow:hidden}' +
      '.mw-head{display:flex;align-items:center;justify-content:space-between;gap:16px}' +
      '.mw-brand{display:flex;align-items:center;gap:0;min-width:0}' +
      '.mw-head .df-logo{margin:0}' +
      '.mw-bits{flex:none;display:block;position:relative;margin-left:-104px;margin-top:-34px}' +
      '.mw-bits text{font-family:ui-monospace,monospace;font-size:9px;fill:' + ACCENT + '}' +
      '.mw-bits .b0{animation-name:mw-b0;animation-iteration-count:infinite;animation-timing-function:ease-in-out}' +
      '.mw-bits .b1{animation-name:mw-b1;animation-iteration-count:infinite;animation-timing-function:ease-in-out}' +
      '.mw-meta{text-align:right;line-height:1.35;padding-top:2px}' +
      '.mw-proj{font-size:12px;color:' + TEXT + '}' +
      '.mw-model{font-size:10.5px;color:' + FAINT + '}' +
      '.mw-rule{height:2px;margin:9px 0 9px;border-radius:2px;' +
        'background:linear-gradient(90deg,transparent,' + ACCENT + ',transparent);' +
        'background-size:40% 100%;background-repeat:no-repeat;opacity:.7;animation:mw-sweep 3.2s linear infinite}' +
      '.mw-metrics{display:flex;flex-wrap:wrap;gap:7px 14px;align-items:baseline}' +
      '.mw-m{display:flex;align-items:baseline;gap:5px}' +
      '.mw-m .v{font-size:16px;font-weight:500;color:' + TEXT + ';font-variant-numeric:tabular-nums}' +
      '.mw-m .v.accent{color:' + ACCENT + '}' +
      '.mw-m .v.warn{color:#FBBF24}' +
      '.mw-m .k{font-size:11px;color:' + DIM + '}' +
      '.mw-foot{margin-top:9px;padding-top:7px;border-top:0.5px solid ' + LINE + ';' +
        'display:flex;flex-wrap:wrap;gap:4px 12px;font-size:11px;color:' + DIM + ';font-variant-numeric:tabular-nums}' +
      '.mw-foot .sep{color:' + FAINT + '}' +
      '.mw-foot b{font-weight:500;color:rgba(244,244,245,.72)}';
    var st = document.createElement("style");
    st.id = "mw-style";
    st.textContent = css;
    document.head.appendChild(st);
  }

  function loadOnce(tag, attr, val, make, cb) {
    var sel = tag + "[" + attr + '="' + val + '"]';
    var ex = document.querySelector(sel);
    if (ex) { if (ex.dataset.mwLoaded || tag === "link") return cb(); ex.addEventListener("load", cb); return; }
    var el = make();
    el.addEventListener("load", function () { el.dataset.mwLoaded = "1"; cb(); });
    el.addEventListener("error", cb);
    document.head.appendChild(el);
  }

  // animate a number from 0 -> target. The final value is ALREADY in the DOM
  // (set by build), so if rAF is throttled/never fires the number is never stuck
  // at 0; the animation is a pure enhancement, with a setTimeout backstop.
  function countUp(el, target, format) {
    var dur = 600, t0 = null;
    function step(ts) {
      if (t0 == null) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      var e = 1 - Math.pow(1 - p, 3); // easeOutCubic
      el.textContent = format(target * e);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = format(target);
    }
    requestAnimationFrame(step);
    setTimeout(function () { el.textContent = format(target); }, dur + 200);
  }

  function build(root, d) {
    var tk = d.tokens || {};
    var fails = Number(d.tool_failures) || 0;
    var agents = Number(d.subagents_launched) || 0;

    root.className = "mw-card";
    root.setAttribute("data-theme", "obsidian");
    root.innerHTML =
      '<div class="mw-head">' +
        '<div class="mw-brand"><div class="mw-logo"></div>' + buildBinary() + '</div>' +
        '<div class="mw-meta"><div class="mw-proj">' + esc(d.project || "") + '</div>' +
          '<div class="mw-model">' + esc(d.model || "") + '</div></div>' +
      '</div>' +
      '<div class="mw-rule"></div>' +
      '<div class="mw-metrics">' +
        '<span class="mw-m"><span class="v accent" data-n="' + (tk.new || 0) + '" data-f="k">' + fmt(tk.new) + '</span><span class="k">токенов</span></span>' +
        '<span class="mw-m"><span class="v" data-money="' + (d.cost_usd || 0) + '">' + money(d.cost_usd) + '</span></span>' +
        '<span class="mw-m"><span class="v">' + esc(d.duration_human || "?") + '</span><span class="k">время</span></span>' +
        '<span class="mw-m"><span class="v" data-n="' + (d.tools_total || 0) + '" data-f="int">' + (d.tools_total || 0) + '</span><span class="k">тулов</span></span>' +
        '<span class="mw-m"><span class="v' + (fails ? " warn" : "") + '" data-n="' + fails + '" data-f="int">' + fails + '</span><span class="k">ошибок</span></span>' +
        '<span class="mw-m"><span class="v" data-n="' + agents + '" data-f="int">' + agents + '</span><span class="k">агентов</span></span>' +
      '</div>' +
      '<div class="mw-foot">' +
        '<span>▲in <b>' + fmt(tk.input) + '</b> ▼out <b>' + fmt(tk.output) + '</b></span>' +
        '<span class="sep">|</span>' +
        '<span>контекст/кэш ⤷<b>' + fmt(tk.cache_read) + '</b> ⤶<b>' + fmt(tk.cache_write) + '</b></span>' +
      '</div>';

    // count-up animations
    root.querySelectorAll(".v[data-n]").forEach(function (el) {
      var target = Number(el.getAttribute("data-n")) || 0;
      var kind = el.getAttribute("data-f");
      countUp(el, target, kind === "int" ? function (x) { return String(Math.round(x)); } : fmt);
    });
    var m = root.querySelector(".v[data-money]");
    if (m) countUp(m, Number(m.getAttribute("data-money")) || 0, money);

    // real denys.fast wordmark, obsidian theme, gentle wind (idle) + entrance
    var slot = root.querySelector(".mw-logo");
    if (g.dfLogo && slot) {
      try {
        slot.style.transform = "scale(.92)";
        slot.style.transformOrigin = "top left";
        var logo = g.dfLogo(slot, { service: "", state: "idle" });
        if (logo && logo.intro) setTimeout(function () { logo.intro(); }, 120);
      } catch (e) { slot.textContent = "denys.fast"; slot.style.color = ACCENT; }
    } else if (slot) {
      slot.textContent = "denys.fast"; slot.style.color = ACCENT; slot.style.fontWeight = "500";
    }
  }

  g.renderMWidget = function (data, mountId) {
    var root = document.getElementById(mountId || "mw");
    if (!root) return;
    var d = (typeof data === "string") ? JSON.parse(data) : (data || {});
    injectStyle();
    // load brand logo assets from the same repo, then build
    loadOnce("link", "data-mw", "logocss",
      function () { var l = document.createElement("link"); l.rel = "stylesheet"; l.href = BASE + "logo.css"; l.setAttribute("data-mw", "logocss"); return l; },
      function () {
        loadOnce("script", "data-mw", "logojs",
          function () { var s = document.createElement("script"); s.src = BASE + "logo.js"; s.setAttribute("data-mw", "logojs"); return s; },
          function () { build(root, d); });
      });
  };
})(window);
