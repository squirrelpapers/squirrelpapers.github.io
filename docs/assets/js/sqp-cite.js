/* Squirrel Papers - citation style switcher (S6).
 *
 * Renders the entry's CSL-JSON (embedded in the page) with citeproc-js and
 * the style chosen in the drop-down. Everything comes from this site: the
 * styles and locales are in sqp-csl-data.js. Without JavaScript, or if
 * anything fails, the pre-rendered citation in the page stays as it is.
 */
(function () {
  "use strict";
  var itemNode = document.getElementById("csl-item");
  var select = document.getElementById("cite-style");
  var out = document.getElementById("cite-text");
  if (!itemNode || !select || !out || !window.CSL || !window.SQP_CSL) { return; }

  var item = JSON.parse(itemNode.textContent);
  var lang = document.documentElement.lang === "de" ? "de-DE" : "en-GB";
  var data = window.SQP_CSL;

  var sys = {
    retrieveLocale: function (id) { return data.locales[id] || data.locales["en-US"]; },
    retrieveItem: function () { return item; }
  };

  function render(style) {
    try {
      var engine = new window.CSL.Engine(sys, data.styles[style], lang, true);
      engine.updateItems([item.id]);
      var bib = engine.makeBibliography();
      out.innerHTML = bib[1].join("").trim();
      // Numeric styles (IEEE, Vancouver) prefix a list number - meaningless
      // for a single entry, and it would end up in the copied text.
      Array.prototype.forEach.call(out.querySelectorAll(".csl-left-margin"), function (n) {
        n.parentNode.removeChild(n);
      });
      out.setAttribute("data-style", style);
    } catch (error) {
      if (window.console) { window.console.warn("citation style", style, error); }
    }
  }

  data.order.forEach(function (key) {
    var option = document.createElement("option");
    option.value = key;
    option.textContent = data.labels[key];
    select.appendChild(option);
  });
  select.value = "apa";
  select.addEventListener("change", function () { render(select.value); });
  document.getElementById("cite-style-field").hidden = false;
  render("apa");
}());
