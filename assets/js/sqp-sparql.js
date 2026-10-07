/* Squirrel Papers - SPARQL page (S9).
 *
 * Pattern from fdo-squirrel-registry: rdflib under Pyodide, no endpoint. Here
 * Pyodide and the rdflib wheels are served from this site
 * (assets/vendor/pyodide/), so nothing is requested from anywhere else, and
 * nothing at all is loaded before the reader starts the engine - by the start
 * button or by the first Run.
 *
 * Results are built with textContent: values come from the graph and from
 * whatever the reader typed, and neither may become markup.
 */
(function () {
  "use strict";
  var CONFIG = JSON.parse(document.getElementById("sparql-config").textContent);
  var UI = CONFIG.ui;
  var startButton = document.getElementById("engine-start");
  var status = document.getElementById("engine-status");
  var engine = null;                     // a Promise of the ready Pyodide instance

  function say(text, state) {
    status.textContent = text;
    status.setAttribute("data-state", state || "");
  }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) { node.className = cls; }
    if (text !== undefined) { node.textContent = text; }
    return node;
  }

  function boot() {
    if (engine) { return engine; }
    startButton.disabled = true;
    if (location.protocol === "file:") {
      say(UI.file_url, "err");
      engine = Promise.reject(new Error(UI.file_url));
      return engine;
    }
    // Absolute: import() resolves a relative path against this script's own
    // URL (assets/js/), not against the page.
    var base = new URL(CONFIG.root + "assets/vendor/pyodide/", document.baseURI).href;
    say(UI.loading_runtime, "busy");
    engine = import(base + "pyodide.mjs").then(function (module) {
      return module.loadPyodide({ indexURL: base });
    }).then(function (py) {
      say(UI.loading_rdflib, "busy");
      // Wheels unpacked directly: no micropip, which would fetch from PyPI.
      return Promise.all(CONFIG.wheels.map(function (name) {
        return fetch(base + name).then(function (r) {
          if (!r.ok) { throw new Error(name + ": HTTP " + r.status); }
          return r.arrayBuffer();
        });
      })).then(function (buffers) {
        buffers.forEach(function (buffer) { py.unpackArchive(buffer, "wheel"); });
        return py;
      });
    }).then(function (py) {
      say(UI.loading_graph, "busy");
      return Promise.all(CONFIG.graphs.map(function (url) {
        return fetch(CONFIG.root + url).then(function (r) {
          if (!r.ok) { throw new Error(url + ": HTTP " + r.status); }
          return r.text();
        });
      })).then(function (texts) {
        py.globals.set("_sqp_texts", texts);
        return py.runPythonAsync([
          "import json",
          "from rdflib import Graph",
          "graph = Graph()",
          "for _text in _sqp_texts.to_py():",
          "    graph.parse(data=_text, format='turtle')",
          "del _sqp_texts",
          "len(graph)"
        ].join("\n")).then(function (n) {
          say(UI.ready.replace("{triples}", n.toLocaleString(CONFIG.lang)), "ok");
          return py;
        });
      });
    });
    engine.catch(function (error) {
      if (location.protocol !== "file:") {
        say(UI.failed + " " + error.message, "err");
        engine = null;                   // allow another attempt
        startButton.disabled = false;
      }
      if (window.console) { window.console.error(error); }
    });
    return engine;
  }

  function table(data, out) {
    if (!data.rows.length) { out.appendChild(el("p", "muted", UI.no_rows)); return; }
    var wrap = el("div", "table-scroll");
    var t = el("table", "result-table");
    var head = el("tr");
    data.cols.forEach(function (c) { head.appendChild(el("th", null, "?" + c)); });
    t.appendChild(el("thead")).appendChild(head);
    var body = el("tbody");
    data.rows.forEach(function (row) {
      var tr = el("tr");
      data.cols.forEach(function (c) {
        var v = row[c];
        var td = el("td");
        if (v === null || v === undefined) { td.className = "nil"; td.textContent = "–"; }
        else if (/^https?:\/\//.test(v)) {
          var a = el("a", null, v);
          a.href = v;
          td.appendChild(a);
        } else { td.textContent = v; }
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
    t.appendChild(body);
    wrap.appendChild(t);
    out.appendChild(wrap);
    out.appendChild(el("p", "small muted", data.total > data.rows.length
      ? UI.rows_first.replace("{shown}", data.rows.length).replace("{n}", data.total)
      : UI.rows.replace("{n}", data.total)));
  }

  function run(id) {
    var button = document.querySelector('[data-run="' + id + '"]');
    var timing = document.getElementById("time-" + id);
    var out = document.getElementById("out-" + id);
    button.disabled = true;
    out.textContent = "";
    timing.textContent = UI.running;
    boot().then(function (py) {
      var t0 = performance.now();
      py.globals.set("_q_src", CONFIG.prefixes + "\n" + document.getElementById("src-" + id).value);
      return py.runPythonAsync([
        "_result = graph.query(_q_src)",
        "_cols = [str(v) for v in _result.vars]",
        "_all = list(_result)",
        "json.dumps({'cols': _cols, 'total': len(_all), 'rows': [",
        "    {c: (None if r[i] is None else str(r[i])) for i, c in enumerate(_cols)}",
        "    for r in _all[:" + CONFIG.max_rows + "]]})"
      ].join("\n")).then(function (json) {
        table(JSON.parse(json), out);
        timing.textContent = UI.time.replace("{s}", ((performance.now() - t0) / 1000).toFixed(2));
      });
    }).catch(function (error) {
      // A malformed query is the normal case on a page meant for editing:
      // show the parser's own message, it says where the mistake is.
      timing.textContent = "";
      // Python tracebacks end with the line that matters; the rest is noise.
      var lines = String(error.message || error).trim().split("\n");
      var start = lines.length - 1;
      while (start > 0 && !/^[A-Za-z_.]*(Error|Exception)\b/.test(lines[start])) { start -= 1; }
      out.appendChild(el("pre", "query-error", lines.slice(start).join("\n")));
    }).then(function () { button.disabled = false; });
  }

  startButton.addEventListener("click", function () { boot(); });
  document.addEventListener("click", function (event) {
    var runner = event.target.closest("[data-run]");
    if (runner) { run(runner.getAttribute("data-run")); return; }
    var reset = event.target.closest("[data-reset]");
    if (reset) {
      var id = reset.getAttribute("data-reset");
      document.getElementById("src-" + id).value = CONFIG.queries[id];
      document.getElementById("out-" + id).textContent = "";
      document.getElementById("time-" + id).textContent = "";
    }
  });
}());
