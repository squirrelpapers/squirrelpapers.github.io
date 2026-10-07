"""Squirrel Papers site pipeline - the single entry point of this repository.

    python main.py                  run every default step, in order
    python main.py --list           print the steps and exit
    python main.py --only site      run one step
    python main.py --from rdf       run this step and everything after it
    python main.py --skip map       run everything except this step
    python main.py --dry-run        print the plan, run nothing
    python main.py --strict         warnings become errors (this is what CI runs)
    python main.py --fresh          forget the step cache: rdf, validate and sparql run
                                    even if their inputs did not change
    python main.py --open           build, then open docs/index.html from disk
    python main.py --serve          build, then serve docs/ on 127.0.0.1:8000
                                    until Ctrl+C (--serve 8080 for another port)

Two kinds of step are NOT part of the default run and only execute when named
with --only:

    migrate   one-off: rewrites content/ from the old Markdown volumes. Once
              content/*.yaml is edited by hand, a default run must never
              overwrite it.
    harvest   reaches the network (Zenodo, Wikidata). Every other step builds
              offline from content/ and data/raw/ (PRIMER A3).

The steps mirror Teil B of PRIMER.md. Until a step is implemented it reports
"skipped (no input)" and the run stays green - that is what makes a bare
`python main.py` a meaningful smoke test from S1 onwards.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import io
import os
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "py"))

REPORT = ROOT / "dist" / "pipeline_report.txt"


class Step(NamedTuple):
    name: str
    module: str          # in py/
    description: str
    default: bool        # part of a bare `python main.py`?
    why_not: str = ""    # shown by --list for non-default steps


STEPS: list[Step] = [
    Step("migrate", "step_migrate", "S2   old Markdown volumes + pub -> content/*.yaml",
         False, "one-off, overwrites content/"),
    Step("harvest", "step_harvest", "S3   Zenodo records, Wikidata places -> data/raw/",
         False, "network"),
    Step("merge", "step_merge", "S4   content/ + data/raw/ -> data/derived/entries.json", True),
    Step("cite", "step_cite", "S6   CSL-JSON, BibTeX, RIS per entry, issue, volume", True),
    Step("rdf", "step_rdf", "S7   DCAT 3 / CRM graph -> dist/", True),
    Step("validate", "step_validate", "S8   SHACL gate", True),
    # sparql checks the example queries against the graph and writes the search
    # index; it writes no HTML - the site step renders both pages (S9).
    Step("sparql", "step_sparql", "S9   search index, example queries checked against the graph", True),
    Step("map", "step_map", "S10  event places -> dist/events.geojson", True),
    Step("model", "step_model", "S16  data model page: diagrams checked against the graph", True),
    # site comes last: it copies the products of cite, rdf, validate, sparql,
    # map and model into docs/ and links them from every page.
    Step("site", "step_site", "S5   render docs/ (EN and DE) for GitHub Pages", True),
]


class Tee(io.TextIOBase):
    """Write to the terminal and to the report file at the same time.

    Steps run in-process, so their prints are captured here rather than through
    a pipe. Report and terminal therefore show exactly the same lines.
    """

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text: str) -> int:
        for stream in self.streams:
            stream.write(text)
            stream.flush()
        return len(text)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Squirrel Papers site.")
    parser.add_argument("--list", action="store_true", help="print steps and exit")
    parser.add_argument("--only", metavar="STEP", help="run this step alone")
    parser.add_argument("--from", dest="start", metavar="STEP", help="start here")
    parser.add_argument("--skip", metavar="STEP", action="append", default=[],
                        help="skip this step (repeatable)")
    parser.add_argument("--dry-run", action="store_true", help="print the plan only")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as errors")
    parser.add_argument("--fresh", action="store_true",
                        help="ignore data/derived/cache/ and rebuild everything")
    parser.add_argument("--open", dest="open_page", action="store_true",
                        help="open docs/index.html in the browser when the run is done")
    parser.add_argument("--serve", nargs="?", const=8000, type=int, metavar="PORT",
                        help="serve docs/ on http://127.0.0.1:PORT (default 8000) "
                             "and open it; Ctrl+C stops it")
    return parser.parse_args()


def select(args: argparse.Namespace) -> list[Step]:
    names = [step.name for step in STEPS]

    for candidate in [args.only, args.start, *args.skip]:
        if candidate and candidate not in names:
            sys.exit(f"unknown step: {candidate}\nknown steps: {', '.join(names)}")

    if args.only:
        return [step for step in STEPS if step.name == args.only]

    chosen = STEPS
    if args.start:
        chosen = chosen[names.index(args.start):]
    # One-off and network steps stay out of a run that did not name them.
    chosen = [step for step in chosen if step.default]
    return [step for step in chosen if step.name not in args.skip]


def run_step(step: Step, strict: bool) -> float:
    """Import the step lazily and run its main(). Returns the duration."""
    started = time.perf_counter()
    module = importlib.import_module(step.module)
    if not hasattr(module, "main"):
        raise AttributeError(f"{step.module} has no main()")

    # Check the signature rather than catching TypeError: a TypeError raised
    # *inside* the step would otherwise be swallowed and the step run twice.
    if "strict" in inspect.signature(module.main).parameters:
        module.main(strict=strict)
    else:
        module.main()
    return time.perf_counter() - started


def show(page: Path) -> None:
    """Open the built page in the default browser, straight off the disk."""
    import webbrowser

    if not page.exists():
        print(f"\nnot opening: {page} does not exist - run the site step first")
        return
    print(f"\nopening {page.as_uri()}")
    webbrowser.open(page.as_uri())


def serve(directory: Path, port: int, page_name: str = "index.html") -> None:
    """Serve docs/ on localhost until Ctrl+C. Nothing is installed or left running.

    Needed for pages that a browser refuses to run from file:// - the SPARQL
    page (Pyodide) and anything that fetches the graph.
    """
    import functools
    import http.server
    import webbrowser

    if not directory.exists():
        print(f"\nnot serving: {directory} does not exist - run the site step first")
        return

    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(directory))
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError as error:
        print(f"\ncannot serve on port {port}: {error}")
        print(f"  another process holds it. On Windows: "
              f"netstat -ano | findstr :{port}   then   taskkill /PID <id> /F")
        return

    url = f"http://127.0.0.1:{port}/{page_name}"
    print(f"\nserving {directory} at {url}")
    print("  press Ctrl+C to stop (nothing is left running afterwards)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped; the port is free again")
    finally:
        server.server_close()


def main() -> int:
    args = parse_args()

    if args.list:
        width = max(len(step.name) for step in STEPS)
        for step in STEPS:
            mark = "" if step.default else f"  [not in default run: {step.why_not}]"
            print(f"  {step.name:<{width}}  {step.description}{mark}")
        return 0

    plan = select(args)
    if not plan:
        print("nothing to do")
        return 0

    if args.dry_run:
        for step in plan:
            print(f"  would run {step.name} ({step.module}): {step.description}")
        return 0

    # Without this, characters such as λ, § and 𝒬 fail at the pipe on Windows
    # and the traceback talks about codecs instead of the actual problem.
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if args.fresh:
        import shutil

        shutil.rmtree(ROOT / "data" / "derived" / "cache", ignore_errors=True)

    timings: list[tuple[str, float]] = []
    failed: str | None = None

    with REPORT.open("w", encoding="utf-8", newline="\n") as log:
        tee = Tee(sys.stdout, log)
        with redirect_stdout(tee), redirect_stderr(tee):
            for step in plan:
                print(f"\n=== {step.name} - {step.description} ===")
                try:
                    timings.append((step.name, run_step(step, args.strict)))
                except Exception:
                    traceback.print_exc()
                    failed = step.name
                    break

            total = sum(duration for _, duration in timings)
            if timings:
                print("\n=== timings ===")
                width = max(len(name) for name, _ in timings)
                for name, duration in timings:
                    share = duration / total * 100 if total else 0
                    print(f"  {name:<{width}}  {duration:6.1f} s  {share:5.1f} %")
                print(f"  {'total':<{width}}  {total:6.1f} s")

            if failed:
                print(f"\nFAILED in step: {failed}")

    if not failed:
        page = ROOT / "docs" / "index.html"
        if args.serve is not None:
            serve(page.parent, args.serve)
        elif args.open_page:
            show(page)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
