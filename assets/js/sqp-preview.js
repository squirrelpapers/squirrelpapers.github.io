/* Squirrel Papers - PDF preview (S8b).
 *
 * Zenodo forbids showing its preview page inside a frame on another site
 * (Content-Security-Policy frame-ancestors), so the PDF itself is fetched from
 * the Zenodo API on request and drawn with pdf.js, served from this site.
 * Nothing is loaded before the reader presses the button. If Zenodo refuses
 * the request, the reader gets the preview on Zenodo in a new tab instead.
 */
(function () {
  "use strict";
  var MAX_PAGES = 30;

  function text(node, value) { node.textContent = value; return node; }

  function fallback(box, button, error) {
    if (window.console) { window.console.warn("PDF preview", error); }
    box.innerHTML = "";
    var p = document.createElement("p");
    p.className = "preview-fallback";
    text(p, button.getAttribute("data-msg-failed") + " ");
    var a = document.createElement("a");
    a.href = button.getAttribute("data-zenodo-preview");
    a.target = "_blank";
    a.rel = "noopener";
    text(a, button.getAttribute("data-msg-open"));
    p.appendChild(a);
    box.appendChild(p);
  }

  function show(button) {
    var box = document.getElementById(button.getAttribute("aria-controls"));
    var root = button.getAttribute("data-root");
    button.disabled = true;
    box.hidden = false;
    text(box, button.getAttribute("data-msg-loading"));

    import(root + "assets/vendor/pdfjs/pdf.min.mjs").then(function (pdfjs) {
      pdfjs.GlobalWorkerOptions.workerSrc = root + "assets/vendor/pdfjs/pdf.worker.min.mjs";
      return pdfjs.getDocument({
        url: button.getAttribute("data-pdf"),
        standardFontDataUrl: root + "assets/vendor/pdfjs/standard_fonts/",
        withCredentials: false
      }).promise;
    }).then(function (pdf) {
      box.innerHTML = "";
      var width = box.clientWidth || 800;
      var count = Math.min(pdf.numPages, MAX_PAGES);
      var chain = Promise.resolve();
      for (var n = 1; n <= count; n += 1) {
        (function (pageNumber) {
          chain = chain.then(function () { return pdf.getPage(pageNumber); }).then(function (page) {
            var base = page.getViewport({ scale: 1 });
            var ratio = window.devicePixelRatio || 1;
            var viewport = page.getViewport({ scale: (width / base.width) * ratio });
            var canvas = document.createElement("canvas");
            canvas.width = Math.floor(viewport.width);
            canvas.height = Math.floor(viewport.height);
            canvas.style.width = "100%";
            canvas.setAttribute("role", "img");
            canvas.setAttribute("aria-label", button.getAttribute("data-msg-page") + " " + pageNumber);
            box.appendChild(canvas);
            return page.render({ canvasContext: canvas.getContext("2d"), viewport: viewport }).promise;
          });
        }(n));
      }
      return chain.then(function () {
        if (pdf.numPages > count) {
          var more = document.createElement("p");
          more.className = "muted small";
          text(more, count + " / " + pdf.numPages + " ");
          var a = document.createElement("a");
          a.href = button.getAttribute("data-download");
          text(a, button.getAttribute("data-msg-download"));
          more.appendChild(a);
          box.appendChild(more);
        }
        box.setAttribute("data-state", "rendered");
      });
    }).catch(function (error) {
      fallback(box, button, error);
      box.setAttribute("data-state", "fallback");
    });
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-pdf]");
    if (button) { show(button); }
  });
}());
