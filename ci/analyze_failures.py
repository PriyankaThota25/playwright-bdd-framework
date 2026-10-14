"""Build reports/failure_analysis.html: which scenarios failed, at which step, and why.

Usage: python3 ci/analyze_failures.py [reports_dir]   (default: reports)

Inputs (reports_dir): junit.xml (pytest) and results.json (written by conftest).
Standard library only, so it runs on the Jenkins container's system python3.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html import escape
from pathlib import Path

LOCATION_RE = re.compile(r"^(?P<file>[\w./\\-]+\.py):(?P<line>\d+):", re.M)
SITE_PACKAGES = ("site-packages", ".ci-venv", "/venv/")

# (reason, likely cause, suggested fix)
ADVICE = {
    "headed": ("Browser launched with a window but no display exists",
               "The run used a config with headless: false (e.g. TEST_ENV=dev) inside the container.",
               "Run with TEST_ENV=ci, or set headless: true."),
    "closed": ("Browser/page closed unexpectedly",
               "Browser crashed, was closed by the test, or failed to start.",
               "Check the Chromium launch logs and container memory/shm."),
    "timeout": ("Timeout waiting for element or navigation",
                "Element never appeared, locator is wrong, or the site was slow/blocked.",
                "Check the locator and the failure screenshot; raise timeout only if the site is just slow."),
    "assert": ("Assertion failed",
               "The page showed something different from what the step expected.",
               "Compare expected vs actual in the error excerpt; check test data and app behaviour."),
    "strict": ("Locator matched multiple elements",
               "The selector is too broad.",
               "Make the locator more specific (role, text, or test id)."),
    "network": ("Network/connection problem",
                "Site unreachable from the Jenkins container, DNS or proxy issue.",
                "Open the base_url from inside the container (docker exec ... curl)."),
    "other": ("Other", "Not matched by a known pattern.", "Read the error excerpt and screenshot."),
}


def classify(error_type: str, text: str) -> str:
    low, et = text.lower(), error_type.lower()
    if "xserver" in low or "missing x server" in low:
        return "headed"
    if "strict mode violation" in low:
        return "strict"
    if "timeout" in et or "timeout" in low:
        return "timeout"
    if "targetclosederror" in et or "has been closed" in low:
        return "closed"
    if "assertionerror" in et or "assert " in low:
        return "assert"
    if "net::err" in low or "connection refused" in low:
        return "network"
    return "other"


def project_location(trace: str) -> str:
    hits = [f"{m['file']}:{m['line']}" for m in LOCATION_RE.finditer(trace)
            if not any(s in m["file"] for s in SITE_PACKAGES)]
    return hits[-1] if hits else "unknown"


def norm(name: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return name[5:] if name.startswith("test_") else name


def load_junit(path: Path) -> tuple[int, dict[str, dict]]:
    if not path.exists():
        return 0, {}
    cases = list(ET.parse(path).getroot().iter("testcase"))
    failures = {}
    for case in cases:
        node = case.find("failure") if case.find("failure") is not None else case.find("error")
        if node is None:
            continue
        trace = node.text or ""
        failures[norm(case.get("name", ""))] = {
            "junit_name": case.get("name", ""),
            "error_type": (node.get("type") or "").split(".")[-1],
            "trace": trace,
            "excerpt": "\n".join(l[1:].strip() for l in trace.splitlines() if l.startswith("E "))[:1500],
        }
    return len(cases), failures


def build(reports: Path) -> dict:
    total, junit = load_junit(reports / "junit.xml")
    rich = []
    rj = reports / "results.json"
    if rj.exists():
        rich = json.loads(rj.read_text(encoding="utf-8")).get("failed", [])

    rows, used = [], set()
    for r in rich:
        key = norm(r["scenario"])
        j = junit.get(key, {})
        used.add(key)
        rows.append({**r, **j_fields(j, r["step_error"])})
    for key, j in junit.items():  # failures without a results.json entry
        if key not in used:
            rows.append({"scenario": j["junit_name"], "feature_file": "", "failed_step": None,
                         "step_error": "", "step_logs": [], "screenshot": None, **j_fields(j, "")})
    return {"total": total, "failed": len(rows), "rows": rows}


def j_fields(j: dict, step_error: str) -> dict:
    trace = j.get("trace", "")
    kind = classify(j.get("error_type", ""), trace + "\n" + step_error)
    reason, cause, fix = ADVICE[kind]
    return {"kind": kind, "reason": reason, "cause": cause, "fix": fix,
            "location": project_location(trace),
            "excerpt": j.get("excerpt") or step_error[:1500]}


CSS = """body{font:14px system-ui,sans-serif;max-width:1000px;margin:24px auto;padding:0 16px;color:#222}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#f4f4f4}.card{border:1px solid #e0b4b4;border-left:5px solid #c62828;border-radius:6px;padding:10px 14px;margin:14px 0}
.card h3{margin:0 0 6px}.k{color:#666;width:130px}pre{background:#f7f7f7;padding:8px;overflow:auto;white-space:pre-wrap}
img{max-width:100%;border:1px solid #ddd;margin-top:6px}.ok{color:#2e7d32}"""


def render(data: dict) -> str:
    if not data["rows"]:
        body = '<p class="ok"><b>No failures.</b></p>'
    else:
        counts = Counter(r["reason"] for r in data["rows"])
        summary = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>" for k, v in counts.items())
        cards = []
        for r in data["rows"]:
            shot = (f'<a href="{escape(r["screenshot"])}"><img src="{escape(r["screenshot"])}" '
                    f'alt="failure screenshot"></a>') if r.get("screenshot") else ""
            logs = "\n".join(r.get("step_logs") or [])
            cards.append(f"""<div class="card"><h3>{escape(r['scenario'])}</h3><table>
<tr><td class="k">Feature file</td><td>{escape(r.get('feature_file') or '-')}</td></tr>
<tr><td class="k">Failed step</td><td>{escape(r.get('failed_step') or 'n/a (failed before/outside a step)')}</td></tr>
<tr><td class="k">Where (code)</td><td>{escape(r['location'])}</td></tr>
<tr><td class="k">Why</td><td><b>{escape(r['reason'])}</b><br>{escape(r['cause'])}</td></tr>
<tr><td class="k">Suggested fix</td><td>{escape(r['fix'])}</td></tr></table>
<details><summary>Error excerpt</summary><pre>{escape(r['excerpt'] or 'none')}</pre></details>
{f'<details><summary>Step logs</summary><pre>{escape(logs)}</pre></details>' if logs else ''}{shot}</div>""")
        body = (f"<h3>By reason</h3><table><tr><th>Reason</th><th>Count</th></tr>{summary}</table>"
                f"<h2>Failed scenarios</h2>{''.join(cards)}")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Failure Analysis</title>'
            f'<style>{CSS}</style></head><body><h1>Failure analysis</h1>'
            f'<p><b>{data["failed"]} failed</b> of {data["total"]} scenarios.</p>{body}</body></html>')


def main() -> int:
    reports = Path(sys.argv[1] if len(sys.argv) > 1 else "reports")
    data = build(reports)
    (reports / "failure_analysis.html").write_text(render(data), encoding="utf-8")
    print(f"Failure analysis: {data['failed']} failed / {data['total']} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
