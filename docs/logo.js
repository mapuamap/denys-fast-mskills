/* ============================================================
   denys.fast — лого-компонент.
   Использование:
     const logo = dfLogo(document.getElementById('slot'), {
       service: 'mb',     // имя сервиса ('' = главный бренд)
       state:   'intro',  // 'intro' | 'idle' | 'work'
     });
     logo.setService('qr');  // заменить имя сервиса
     logo.setState('work');  // переключить состояние
     logo.intro();           // проиграть появление (затем само вернётся в idle)
   ============================================================ */
(function (global) {
  'use strict';

  // ветер: [top, width, height, длительность s, задержка s, пик opacity]
  var WINDS = [
    [14, 90, 4, .51, .00, .28],
    [36, 60, 3, .64, .22, .21],
    [60, 110, 5, .47, .38, .32],
    [82, 70, 3, .60, .10, .21],
    [102, 95, 4, .55, .48, .28],
    [146, 85, 4, .51, .58, .25],
  ];
  // пыль: [top, диаметр, длительность s, задержка s, пик opacity]
  var DUSTS = [
    [24, 4, .55, .12, .30],
    [50, 3, .68, .40, .25],
    [72, 5, .50, .25, .32],
    [95, 3, .60, .55, .25],
    [118, 4, .72, .05, .28],
    [140, 3, .58, .33, .22],
    [10, 3, .65, .48, .20],
  ];

  function particles(cls, items, round) {
    var html = '<div class="' + cls + '">';
    items.forEach(function (p) {
      var w = p[1], h = round ? p[1] : p[2], i = round ? 1 : 2;
      html += '<i style="top:' + p[0] + 'px;left:' + (442 - w) + 'px;width:' + w +
              'px;height:' + h + 'px;--t:' + p[i + 1] + 's;--d:' + p[i + 2] +
              's;--o:' + p[i + 3] + '"></i>';
    });
    return html + '</div>';
  }

  var MARK =
    '<div class="stage"><div class="mark">' +
    particles('wind', WINDS, false) +
    particles('wind dust', DUSTS, true) +
    '<div class="ly lt"></div><div class="ly lm"></div><div class="ly lb"></div>' +
    '<div class="ly cb"></div><div class="ly cf"></div>' +
    '</div></div>';

  function letterSpans(service) {
    var word = (service ? service + '.' : '') + 'denys.fast';
    var n = word.length;
    var fastStart = word.lastIndexOf('.') + 1;
    var svcEnd = service ? service.length : -1;
    var out = '';
    for (var i = 0; i < n; i++) {
      var ch = word[i];
      var cls = 'ch';
      if (ch === '.') cls += ' dot';
      else if (i < svcEnd) cls += ' svc';
      else if (i >= fastStart) cls += ' fast';
      else cls += ' den';
      var c = Math.abs(i - (n - 1) / 2);
      out += '<span class="' + cls + '" style="--i:' + i + ';--c:' + c + '">' + ch + '</span>';
    }
    return out;
  }

  function introDuration(service) {
    var len = ((service ? service + '.' : '') + 'denys.fast').length;
    return 620 + len * 50 + 400; // старт букв + стаггер + хвост
  }

  function dfLogo(el, opts) {
    opts = opts || {};
    var service = opts.service || '';
    var state = 'idle';
    var timer = null;

    el.classList.add('df-logo');

    function render() {
      el.innerHTML = MARK + '<div class="word">' + letterSpans(service) + '</div>';
      el.classList.toggle('has-svc', !!service);
    }

    function applyState(s) {
      el.classList.remove('a-idle', 'a-race', 'a-work', 'play');
      state = s;
      if (s === 'idle') el.classList.add('a-idle');
      else if (s === 'work') el.classList.add('a-work');
      else if (s === 'intro') el.classList.add('a-race');
    }

    function startIntroPlay() {
      void el.offsetWidth; // reflow — рестарт анимации
      el.classList.add('play');
      timer = setTimeout(function () { setState('idle'); }, introDuration(service));
    }

    // Плавный переход: заморозить текущую позу -> довести transition'ом
    // до базовой позы нового состояния -> запустить его анимации.
    function setState(s, instant) {
      clearTimeout(timer);
      var settleTimer;
      if (instant) {
        applyState(s);
        if (s === 'intro') startIntroPlay();
        return;
      }
      var parts = el.querySelectorAll('.ly, .ch, .stage, .wind i');
      parts.forEach(function (p) {
        var cs = getComputedStyle(p);
        p.style.opacity = cs.opacity;
        if (cs.transform !== 'none') p.style.transform = cs.transform;
      });
      el.classList.add('no-anim');   // стоп анимаций, поза держится инлайном
      applyState(s);
      void el.offsetWidth;
      el.classList.add('settle');    // включить transition
      parts.forEach(function (p) {   // отпустить к базовой позе нового состояния
        p.style.opacity = '';
        p.style.transform = '';
      });
      settleTimer = setTimeout(function () {
        el.classList.remove('no-anim', 'settle');
        if (s === 'intro') startIntroPlay();
      }, 300);
      timer = settleTimer;
    }

    function setService(name) {
      service = name || '';
      render();
      setState(state === 'intro' ? 'intro' : state);
    }

    render();
    setState(opts.state || 'idle', true); // первый запуск — без перехода

    return {
      el: el,
      setState: setState,
      setService: setService,
      intro: function () { setState('intro'); },
      getService: function () { return service; },
    };
  }

  global.dfLogo = dfLogo;
})(window);
