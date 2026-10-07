/* Squirrel Papers - map of conference places (S10).
 *
 * Data: window.SQP_EVENTS (map/events.js, written by py/step_map.py from the
 * graph) and window.SQP_COUNTRIES (Natural Earth, served from this site). The
 * map is complete without anyone else's server; OpenStreetMap tiles are added
 * only when the reader switches them on, and removed again on request.
 *
 * One circle per place, sized by the number of entries presented there; its
 * popup lists the events at that place and their entries. Text from the data
 * goes in with textContent only.
 */
(function () {
  "use strict";
  var EVENTS = window.SQP_EVENTS, COUNTRIES = window.SQP_COUNTRIES, L = window.L;
  var box = document.getElementById("map");
  if (!EVENTS || !L || !box) { return; }
  var UI = JSON.parse(document.getElementById("map-ui").textContent);
  var tools = document.getElementById("map-tools");
  var yearSelect = document.getElementById("map-year");
  var osmButton = document.getElementById("map-osm");

  box.hidden = false;
  tools.hidden = false;
  // Leaflet draws nothing into a box without height. The stylesheet gives it
  // one; should an old cached stylesheet arrive with a new page, this does.
  if (box.clientHeight < 100) { box.style.height = "480px"; }
  var colour = function (name, fallback) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
  };

  var map = L.map(box, { worldCopyJump: true, minZoom: 2, maxZoom: 16, zoomSnap: 0.5 });
  map.attributionControl.setPrefix(false);
  function landStyle() {
    return { color: colour("--map-border", "#b9a9b5"), weight: 0.7,
             fillColor: colour("--map-land", "#f6f1f5"), fillOpacity: 1 };
  }
  var land = null;
  if (COUNTRIES) {
    land = L.geoJSON(COUNTRIES, { interactive: false, style: landStyle }).addTo(map);
    map.attributionControl.addAttribution("Natural Earth");
  }
  box.style.background = colour("--map-sea", "#dfe9f0");
  // The light/dark switch (base template) repaints land and sea.
  document.addEventListener("sqp-theme", function () {
    if (land) { land.setStyle(landStyle()); }
    box.style.background = colour("--map-sea", "#dfe9f0");
  });

  var osm = null;
  osmButton.addEventListener("click", function () {
    if (osm) {
      map.removeLayer(osm);
      osm = null;
      osmButton.textContent = osmButton.getAttribute("data-show");
      return;
    }
    osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    osmButton.textContent = osmButton.getAttribute("data-hide");
  });

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) { node.className = cls; }
    if (text !== undefined) { node.textContent = text; }
    return node;
  }
  var dateFormat = new Intl.DateTimeFormat(UI.lang === "de" ? "de-DE" : "en-GB",
    { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  function when(p) {
    if (!p.start) { return ""; }
    var start = dateFormat.format(new Date(p.start + "T00:00:00Z"));
    if (!p.end || p.end === p.start) { return start; }
    return start + " – " + dateFormat.format(new Date(p.end + "T00:00:00Z"));
  }

  function popup(place, features) {
    var root = el("div", "map-popup");
    var head = el("p", "map-popup-place");
    if (place.wikidata) {
      var a = el("a", null, place.label);
      a.href = "https://www.wikidata.org/wiki/" + place.wikidata;
      head.appendChild(a);
    } else { head.textContent = place.label; }
    root.appendChild(head);
    features.forEach(function (f) {
      var p = f.properties;
      root.appendChild(el("p", "map-popup-event", p.name));
      if (p.start) { root.appendChild(el("p", "map-popup-date", when(p))); }
      var list = el("ul", "plain");
      p.entries.forEach(function (e) {
        var li = el("li");
        var link = el("a");
        link.href = UI.home + e.path + "/";
        link.appendChild(el("span", "sigil", e.label));
        link.appendChild(document.createTextNode(" " + e.title));
        li.appendChild(link);
        list.appendChild(li);
      });
      root.appendChild(list);
    });
    return root;
  }

  var layer = L.featureGroup().addTo(map);
  function draw(year) {
    layer.clearLayers();
    var places = {};
    EVENTS.features.forEach(function (f) {
      if (year && (f.properties.start || "").slice(0, 4) !== year) { return; }
      var key = f.properties.place.iri;
      (places[key] = places[key] || { place: f.properties.place, at: f.geometry.coordinates, features: [] })
        .features.push(f);
    });
    Object.keys(places).sort().forEach(function (key) {
      var group = places[key];
      var n = group.features.reduce(function (sum, f) { return sum + f.properties.entries.length; }, 0);
      L.circleMarker([group.at[1], group.at[0]], {
        radius: 5 + 3 * Math.sqrt(n),
        color: "#ffffff", weight: 1.5,
        fillColor: colour("--sqp-berry", "#b03686"), fillOpacity: 0.85
      }).bindPopup(popup(group.place, group.features), { maxWidth: 340 })
        .bindTooltip(group.place.label + " (" + n + ")")
        .addTo(layer);
    });
    // Most places are in Europe; one in Colorado would otherwise shrink
    // Europe to a corner. Fit to Europe when it holds most of what is shown;
    // the others stay on the map, one zoom step out.
    var all = layer.getLayers(), europe = all.filter(function (m) {
      var at = m.getLatLng();
      return at.lat > 34 && at.lat < 72 && at.lng > -25 && at.lng < 45;
    });
    var shown = europe.length >= 0.8 * all.length ? europe : all;
    if (shown.length) { map.fitBounds(L.featureGroup(shown).getBounds().pad(0.15), { maxZoom: 7 }); }
  }

  yearSelect.addEventListener("change", function () { draw(yearSelect.value); });
  map.setView([50, 10], 4);
  draw("");
}());
