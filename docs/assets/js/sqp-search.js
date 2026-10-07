/* Squirrel Papers - search page (S9).
 *
 * Runs over window.SQP_INDEX (search/index.js, written by py/step_sparql.py).
 * Text: every word typed must occur in the entry, ignoring case and accents.
 * Facets: values within one facet are alternatives (OR), facets combine (AND);
 * each facet counts what the other filters leave, so a count never promises a
 * result that clicking would not deliver. The state lives in the URL hash
 * (#type=poster&year=2019&q=wikidata), so a filtered view can be shared.
 * Everything is built with textContent - entry data never becomes markup.
 */
(function () {
  "use strict";
  var INDEX = window.SQP_INDEX;
  var root = document.getElementById("search");
  if (!INDEX || !root) { return; }
  var UI = JSON.parse(document.getElementById("search-ui").textContent);
  var LANG = UI.lang;
  var SHOW = 8;                          // facet values shown before "Show all"

  var input = document.getElementById("search-text");
  var facetBox = document.getElementById("search-facets");
  var list = document.getElementById("search-results");
  var count = document.getElementById("search-count");
  var state = { q: "", filters: {} };
  var expanded = {};

  function fold(text) {
    return String(text).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }
  INDEX.entries.forEach(function (e) { e._text = fold(e.text); });

  function label(facet, value) {
    var l = INDEX.labels[facet][value];
    if (l && typeof l === "object") { return l[LANG] || l.en || value; }
    return l || value;
  }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) { node.className = cls; }
    if (text !== undefined) { node.textContent = text; }
    return node;
  }

  function matchesText(e, words) {
    for (var i = 0; i < words.length; i += 1) {
      if (e._text.indexOf(words[i]) === -1) { return false; }
    }
    return true;
  }
  function matchesFacets(e, skip) {
    for (var facet in state.filters) {
      if (facet === skip || !state.filters[facet].length) { continue; }
      var values = e.facets[facet], hit = false;
      for (var i = 0; i < values.length && !hit; i += 1) {
        hit = state.filters[facet].indexOf(values[i]) !== -1;
      }
      if (!hit) { return false; }
    }
    return true;
  }

  function order(facet, counts) {
    var keys = Object.keys(counts);
    if (facet === "year") { return keys.sort().reverse(); }
    if (facet === "volume") { return keys.sort(function (a, b) { return b - a; }); }
    return keys.sort(function (a, b) {
      return counts[b] - counts[a] || label(facet, a).localeCompare(label(facet, b));
    });
  }

  function renderFacets(textHits) {
    facetBox.textContent = "";
    INDEX.facets.forEach(function (facet) {
      var counts = {};
      textHits.forEach(function (e) {
        if (!matchesFacets(e, facet)) { return; }
        e.facets[facet].forEach(function (v) { counts[v] = (counts[v] || 0) + 1; });
      });
      var chosen = state.filters[facet] || [];
      chosen.forEach(function (v) { if (!(v in counts)) { counts[v] = 0; } });
      var keys = order(facet, counts);
      if (!keys.length) { return; }

      var group = el("fieldset", "facet");
      group.appendChild(el("legend", null, UI.facets[facet]));
      var limit = expanded[facet] ? keys.length : Math.max(SHOW, chosen.length);
      keys.forEach(function (value, i) {
        if (i >= limit && chosen.indexOf(value) === -1) { return; }
        var row = el("label", "facet-value");
        var box = el("input");
        box.type = "checkbox";
        box.checked = chosen.indexOf(value) !== -1;
        box.addEventListener("change", function () { toggle(facet, value); });
        row.appendChild(box);
        row.appendChild(el("span", "facet-label", label(facet, value)));
        row.appendChild(el("span", "facet-count", String(counts[value])));
        group.appendChild(row);
      });
      if (keys.length > SHOW) {
        var more = el("button", "facet-more",
          expanded[facet] ? UI.fewer : UI.more.replace("{n}", keys.length));
        more.type = "button";
        more.addEventListener("click", function () { expanded[facet] = !expanded[facet]; update(false); });
        group.appendChild(more);
      }
      facetBox.appendChild(group);
    });
  }

  function renderResults(hits) {
    list.textContent = "";
    count.textContent = hits.length === 1 ? UI.one : UI.many.replace("{n}", hits.length);
    if (!hits.length) { list.appendChild(el("li", "muted", UI.none)); return; }
    hits.forEach(function (e) {
      var li = el("li", "result");
      li.appendChild(el("span", "result-label", e.label));
      var body = el("div", "result-body");
      var a = el("a", "entry-item-title", e.title);
      a.href = UI.home + e.path + "/";
      body.appendChild(a);
      var meta = el("div", "entry-item-meta");
      e.facets.type.forEach(function (slug) {
        meta.appendChild(el("span", "badge", label("type", slug)));
        meta.appendChild(document.createTextNode(" "));
      });
      var who = e.authors.slice(0, 3).join(", ") + (e.authors.length > 3 ? " et al." : "");
      meta.appendChild(el("span", null, [who, e.date].filter(Boolean).join(" · ")));
      if (e.facets.event.length) { meta.appendChild(el("span", "muted", " · " + e.facets.event[0])); }
      body.appendChild(meta);
      li.appendChild(body);
      list.appendChild(li);
    });
  }

  function writeHash() {
    var parts = [];
    if (state.q) { parts.push("q=" + encodeURIComponent(state.q)); }
    INDEX.facets.forEach(function (f) {
      if ((state.filters[f] || []).length) {
        parts.push(f + "=" + state.filters[f].map(encodeURIComponent).join(","));
      }
    });
    var hash = parts.length ? "#" + parts.join("&") : "";
    if (hash !== location.hash) {
      history.replaceState(null, "", location.pathname + location.search + hash);
    }
  }
  function readHash() {
    state = { q: "", filters: {} };
    location.hash.replace(/^#/, "").split("&").forEach(function (part) {
      var kv = part.split("="), key = kv[0], value = kv.slice(1).join("=");
      if (!value) { return; }
      if (key === "q") { state.q = decodeURIComponent(value); }
      else if (INDEX.facets.indexOf(key) !== -1) {
        state.filters[key] = value.split(",").map(decodeURIComponent);
      }
    });
    input.value = state.q;
  }

  function update(hash) {
    var words = fold(state.q).split(/\s+/).filter(Boolean);
    var textHits = INDEX.entries.filter(function (e) { return matchesText(e, words); });
    renderFacets(textHits);
    renderResults(textHits.filter(function (e) { return matchesFacets(e, null); }));
    if (hash !== false) { writeHash(); }
  }
  function toggle(facet, value) {
    var chosen = state.filters[facet] = state.filters[facet] || [];
    var at = chosen.indexOf(value);
    if (at === -1) { chosen.push(value); } else { chosen.splice(at, 1); }
    update();
  }

  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { state.q = input.value.trim(); update(); }, 120);
  });
  document.getElementById("search-clear").addEventListener("click", function () {
    state = { q: "", filters: {} };
    input.value = "";
    update();
    input.focus();
  });
  window.addEventListener("hashchange", function () { readHash(); update(false); });

  // On a phone the filters would push every result below the fold: closed
  // there, open from the two-column width up (same breakpoint as the CSS).
  if (window.matchMedia && !window.matchMedia("(min-width: 860px)").matches) {
    document.getElementById("search-panel").open = false;
  }
  root.hidden = false;
  readHash();
  update(false);
}());
