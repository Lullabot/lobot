// Shared behavior for every page of the Lobot site. No dependencies.
(function () {
  // Skill filters
  var buttons = document.querySelectorAll('.filter');
  var items = document.querySelectorAll('#skill-list [data-group]');
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-filter');
      buttons.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      items.forEach(function (el) { el.hidden = !(f === 'all' || el.getAttribute('data-group') === f); });
    });
  });

  // Core record tabs
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.rec-tab'));
  function select(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      if (panel) panel.hidden = !on;
    });
    if (focus) tab.focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { select(t); });
    t.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (d) { e.preventDefault(); select(tabs[(i + d + tabs.length) % tabs.length], true); }
    });
  });

  // Skill count from the cards, so the number never drifts
  var count = document.querySelectorAll('[data-skill]').length;
  document.querySelectorAll('[data-count="skills"]').forEach(function (el) { el.textContent = count; });

  // Copy buttons
  document.querySelectorAll('.copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var copy = document.getElementById(btn.getAttribute('data-copy')).cloneNode(true);
      copy.querySelectorAll('[hidden]').forEach(function (h) { h.remove(); }); // only the reader's chosen level
      var text = copy.textContent;
      var done = function () { btn.textContent = 'Copied'; setTimeout(function () { btn.textContent = 'Copy'; }, 1600); };
      if (navigator.clipboard) { navigator.clipboard.writeText(text).then(done, function () {}); }
    });
  });

  // Comfort level (Get started): one choice for the whole page, remembered per browser
  var levelTabs = document.querySelectorAll('.level-tab');
  function setLevel(level) {
    levelTabs.forEach(function (t) { t.setAttribute('aria-selected', t.getAttribute('data-level') === level ? 'true' : 'false'); });
    document.querySelectorAll('[data-level]:not(.level-tab)').forEach(function (el) { el.hidden = el.getAttribute('data-level') !== level; });
    try { localStorage.setItem('lobot-level', level); } catch (e) {}
  }
  if (levelTabs.length) {
    levelTabs.forEach(function (t) { t.addEventListener('click', function () { setLevel(t.getAttribute('data-level')); }); });
    var saved = null;
    try { saved = localStorage.getItem('lobot-level'); } catch (e) {}
    setLevel(saved === 'checklist' || saved === 'terminal' ? saved : 'step');
  }

  // Live version and release notes from GitHub
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function line(text) {
    text = text.replace(/\s*\(\[[0-9a-f]{7}\]\([^)]*\)\)/g, '')      // commit link
               .replace(/,?\s*closes\s+(\[#\d+\]\([^)]*\)\s*)+/g, ''); // issue links
    var scope = '';
    var m = text.match(/^\*\*([^*]+):\*\*\s*/);
    if (m) { scope = '<span class="scope">' + esc(m[1]) + '</span>'; text = text.slice(m[0].length); }
    return scope + esc(text);
  }
  function render(body) {
    var html = '', open = false, seen = {};
    (body || '').split(/\r?\n/).forEach(function (raw) {
      var l = raw.trim();
      if (/^#{3,}\s/.test(l)) {
        if (open) { html += '</ul>'; open = false; }
        html += '<h4>' + esc(l.replace(/^#+\s*/, '')) + '</h4>';
      } else if (/^[*-]\s/.test(l)) {
        var item = line(l.slice(2));
        if (seen[item]) return; // a change merged twice shows once
        seen[item] = true;
        if (!open) { html += '<ul>'; open = true; }
        html += '<li>' + item + '</li>';
      }
    });
    if (open) html += '</ul>';
    return html;
  }
  fetch('https://api.github.com/repos/Lullabot/lobot/releases?per_page=3', { headers: { Accept: 'application/vnd.github+json' } })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (list) {
      if (!list.length) throw new Error('none');
      var v = document.getElementById('version');
      if (v) { v.querySelector('span:last-child').textContent = list[0].tag_name; v.hidden = false; }
      var box = document.getElementById('releases');
      if (!box) return;
      var out = list.map(function (rel) {
        var date = new Date(rel.published_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
        return '<article class="release"><header><a href="' + esc(rel.html_url) + '">' + esc(rel.tag_name) + '</a><time datetime="' + esc(rel.published_at) + '">' + date + '</time></header>' + render(rel.body) + '</article>';
      }).join('');
      box.innerHTML = out;
    })
    .catch(function () {
      var box = document.getElementById('releases');
      if (box) box.innerHTML = '<p class="muted">Couldn\'t load the latest releases right now. Read them in the <a href="https://github.com/Lullabot/lobot/blob/main/CHANGELOG.md">changelog</a>.</p>';
    });
})();
