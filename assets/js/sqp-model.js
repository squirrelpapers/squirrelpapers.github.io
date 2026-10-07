/* Squirrel Papers - data model page (S16).
 *
 * Draws the Mermaid diagrams with the copy of Mermaid served from this site.
 * Node colours are fixed in the diagrams themselves (classDef); lines, edge
 * labels and text follow the page's light or dark colours, and are redrawn
 * when the reader flips the light/dark switch. Without JavaScript, or should
 * Mermaid fail, the diagram source stays readable in its <pre>.
 */
(function () {
  "use strict";
  var mermaid = window.mermaid;
  if (!mermaid) { return; }
  var blocks = Array.prototype.slice.call(document.querySelectorAll("pre.mermaid"));
  var sources = blocks.map(function (pre) { return pre.textContent; });

  function draw() {
    var css = getComputedStyle(document.documentElement);
    function v(name, fallback) { return css.getPropertyValue(name).trim() || fallback; }
    var text = v("--text", "#1d141b"), bg = v("--bg", "#ffffff");
    blocks.forEach(function (pre, i) {
      pre.removeAttribute("data-processed");
      pre.textContent = sources[i];
    });
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: "base",
      themeVariables: {
        background: bg,
        lineColor: v("--text-muted", "#5c4f59"),
        textColor: text,
        primaryTextColor: text,
        edgeLabelBackground: bg,
        clusterBkg: bg,
        fontFamily: v("--font-body", "sans-serif"),
        fontSize: "14px"
      },
      flowchart: { curve: "basis", htmlLabels: true, useMaxWidth: true }
    });
    mermaid.run({ nodes: blocks }).catch(function (error) {
      if (window.console) { window.console.error("Mermaid", error); }
    });
  }

  document.addEventListener("sqp-theme", draw);
  draw();
}());
