from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from html import escape
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORT_FILE = REPORTS_DIR / "custom_test_report.html"


@dataclass
class StepResult:
    keyword: str
    name: str
    status: str  # "passed" | "failed"
    logs: list[str] = field(default_factory=list)
    screenshot: Path | None = None
    error: str | None = None


@dataclass
class ScenarioResult:
    name: str
    feature_name: str
    feature_file: str
    status: str = "passed"  # "passed" | "failed" | "skipped"
    duration: float = 0.0
    steps: list[StepResult] = field(default_factory=list)
    error: str | None = None  # set when the scenario failed before any step ran


@dataclass
class FeatureResult:
    name: str
    filename: str
    scenarios: list[ScenarioResult] = field(default_factory=list)

    @property
    def status(self) -> str:
        statuses = {s.status for s in self.scenarios}
        if "failed" in statuses:
            return "failed"
        if statuses == {"skipped"}:
            return "skipped"
        return "passed"

    @property
    def passed_count(self) -> int:
        return sum(1 for s in self.scenarios if s.status == "passed")


@dataclass
class RunMeta:
    browser_name: str = "-"
    browser_version: str = "-"
    playwright_version: str = "-"
    python_version: str = "-"
    start_time: datetime | None = None
    end_time: datetime | None = None

    @staticmethod
    def _fmt(dt: datetime | None) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "-"

    @property
    def start_display(self) -> str:
        return self._fmt(self.start_time)

    @property
    def end_display(self) -> str:
        return self._fmt(self.end_time)

    @property
    def duration_display(self) -> str:
        if not (self.start_time and self.end_time):
            return "-"
        total_seconds = int((self.end_time - self.start_time).total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}h {minutes}m {seconds}s"
        if minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"


def _group_by_feature(results: list[ScenarioResult]) -> list[FeatureResult]:
    features: dict[str, FeatureResult] = {}
    for result in results:
        feature = features.setdefault(
            result.feature_file,
            FeatureResult(name=result.feature_name, filename=result.feature_file),
        )
        feature.scenarios.append(result)
    return list(features.values())


_STYLE = """
:root {
  --passed: #1a7f37; --passed-2: #2ea043; --failed: #cf222e; --failed-2: #e5534b;
  --skipped: #9a6700; --skipped-2: #d4a72c;
  --border: #d0d7de; --bg-soft: #f6f8fa; --bg-page: #f3f5fb; --card: #fff; --text: #1f2328;
  --text-muted: #656d76; --accent: #6e40c9; --accent-2: #0969da; --accent-3: #d63384;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  margin: 0; color: var(--text);
  background:
    radial-gradient(900px 420px at 15% -10%, rgba(110,64,201,.10), transparent 60%),
    radial-gradient(900px 420px at 85% -10%, rgba(9,105,218,.10), transparent 60%),
    var(--bg-page);
}
.page { max-width: 1120px; margin-inline: auto; padding: 0 24px 40px; }

.page-header {
  background: linear-gradient(120deg, var(--accent) 0%, var(--accent-2) 55%, var(--accent-3) 130%);
  color: #fff; padding: 36px 24px; margin-bottom: -1px; text-align: center;
  box-shadow: 0 6px 24px rgba(9,105,218,.25); position: relative; overflow: hidden;
}
.page-header::before {
  content: ""; position: absolute; inset: 0;
  background: radial-gradient(500px 200px at 50% 0%, rgba(255,255,255,.18), transparent 70%);
}
.page-header .inner { max-width: 1120px; margin-inline: auto; position: relative; }
.page-header h1 { margin: 0 0 6px; font-size: 28px; font-weight: 800; letter-spacing: -.01em; text-shadow: 0 1px 2px rgba(0,0,0,.1); }
.page-header .subtitle { margin: 0; opacity: .9; font-size: 13px; }

.overview {
  display: grid; grid-template-columns: 1.3fr 1fr; gap: 16px;
  margin-top: 24px; margin-bottom: 20px;
}
@media (max-width: 760px) { .overview { grid-template-columns: 1fr; } }

.card {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 18px 20px; box-shadow: 0 1px 2px rgba(16,24,40,.04);
  transition: transform .18s ease, box-shadow .18s ease;
}
.card:hover {
  transform: translateY(-3px) scale(1.015);
  box-shadow: 0 10px 28px rgba(16,24,40,.14);
}
.card h2 { margin: 0 0 14px; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; color: var(--text-muted); }

.meta-section h2 {
  margin: 0 0 12px; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; color: var(--text-muted);
}
.stat-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(128px, 1fr)); gap: 12px;
}
.stat-card {
  border-radius: 12px; padding: 14px 16px; border: 1px solid transparent;
  transition: transform .18s ease, box-shadow .18s ease;
}
.stat-card:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 10px 24px rgba(16,24,40,.12);
}
.stat-label {
  font-size: 10.5px; text-transform: uppercase; letter-spacing: .04em;
  color: var(--stat-fg, var(--text-muted)); opacity: .8; margin-bottom: 4px;
}
.stat-value { font-size: 14.5px; font-weight: 700; color: var(--stat-fg, var(--text)); word-break: break-word; }

.stat-c1 { background: linear-gradient(135deg, #e0e7ff, #c7d2fe); border-color: #c7d2fe; --stat-fg: #4338ca; }
.stat-c2 { background: linear-gradient(135deg, #cffafe, #a5f3fc); border-color: #a5f3fc; --stat-fg: #0e7490; }
.stat-c3 { background: linear-gradient(135deg, #dcfce7, #bbf7d0); border-color: #bbf7d0; --stat-fg: #15803d; }
.stat-c4 { background: linear-gradient(135deg, #fef9c3, #fde68a); border-color: #fde68a; --stat-fg: #92400e; }
.stat-c5 { background: linear-gradient(135deg, #fae8ff, #f5d0fe); border-color: #f5d0fe; --stat-fg: #a21caf; }
.stat-c6 { background: linear-gradient(135deg, #ffe4e6, #fecdd3); border-color: #fecdd3; --stat-fg: #be123c; }
.stat-c7 { background: linear-gradient(135deg, #ffedd5, #fed7aa); border-color: #fed7aa; --stat-fg: #c2410c; }
.stat-c8 { background: linear-gradient(135deg, #e0f2fe, #bae6fd); border-color: #bae6fd; --stat-fg: #0369a1; }

.chart-card { border-top: 4px solid var(--accent-2); }
.chart-card .chart-wrap { display: flex; align-items: center; gap: 22px; flex-wrap: wrap; }
.pie {
  width: 128px; height: 128px; border-radius: 50%; flex-shrink: 0;
  background: var(--pie-bg, conic-gradient(var(--border) 0 100%));
  display: flex; align-items: center; justify-content: center;
  position: relative; box-shadow: 0 4px 14px rgba(16,24,40,.12);
}
.pie::before {
  content: ""; position: absolute; inset: 16px; background: var(--card); border-radius: 50%;
  box-shadow: inset 0 1px 3px rgba(16,24,40,.08);
}
.pie-center { position: relative; display: flex; flex-direction: column; align-items: center; line-height: 1.1; }
.pie-center strong { font-size: 20px; }
.pie-center span { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .03em; }

.legend { list-style: none; margin: 0; padding: 0; font-size: 13px; display: flex; flex-direction: column; gap: 8px; }
.legend li {
  display: flex; align-items: center; gap: 8px; padding: 5px 10px; border-radius: 8px;
  background: var(--bg-soft); border: 1px solid var(--border);
}
.legend b { margin-left: 2px; }
.legend .pct { color: var(--text-muted); margin-left: 4px; }
.dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 0 3px rgba(0,0,0,.04); }
.dot.passed { background: linear-gradient(135deg, var(--passed-2), var(--passed)); }
.dot.failed { background: linear-gradient(135deg, var(--failed-2), var(--failed)); }
.dot.skipped { background: linear-gradient(135deg, var(--skipped-2), var(--skipped)); }

.controls {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  flex-wrap: wrap; margin-bottom: 18px;
}
.tabs {
  display: flex; gap: 6px; background: linear-gradient(180deg, #eef1fb, var(--bg-soft));
  border: 1px solid var(--border); border-radius: 10px; padding: 4px;
}
.tab {
  border: none; background: transparent; padding: 7px 14px; border-radius: 7px; font-size: 13px;
  font-weight: 600; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; gap: 6px;
  transition: background .15s ease, color .15s ease;
}
.tab:hover { color: var(--text); background: rgba(255,255,255,.6); }
.tab.active { background: var(--card); color: var(--text); box-shadow: 0 2px 6px rgba(16,24,40,.1); }
.tab .count {
  background: var(--border); color: var(--text-muted); font-size: 11px; font-weight: 700;
  padding: 1px 7px; border-radius: 999px;
}
.tab.active .count { background: var(--accent-2); color: #fff; }
.tab[data-filter="failed"].active .count { background: var(--failed); }
.tab[data-filter="passed"].active .count { background: var(--passed); }

.search-wrap { position: relative; flex: 0 1 280px; min-width: 200px; }
.search-wrap input {
  width: 100%; padding: 9px 12px 9px 34px; border: 1px solid var(--border); border-radius: 8px;
  font-size: 13px; background: var(--card); color: var(--text); transition: box-shadow .15s ease, border-color .15s ease;
}
.search-wrap input:focus {
  outline: none; border-color: var(--accent-2); box-shadow: 0 0 0 3px rgba(9,105,218,.15);
}
.search-wrap::before {
  content: "🔍"; position: absolute; left: 11px; top: 50%; transform: translateY(-50%);
  font-size: 12px; opacity: .55;
}

.badge {
  font-size: 10px; font-weight: 700; padding: 2px 9px; border-radius: 999px;
  color: #fff; letter-spacing: .04em; white-space: nowrap; box-shadow: 0 1px 2px rgba(16,24,40,.15);
}
.badge.passed { background: linear-gradient(135deg, var(--passed-2), var(--passed)); }
.badge.failed { background: linear-gradient(135deg, var(--failed-2), var(--failed)); }
.badge.skipped { background: linear-gradient(135deg, var(--skipped-2), var(--skipped)); }

details.feature {
  border: 1px solid var(--border); border-top: 4px solid var(--border); border-radius: 12px;
  margin-bottom: 16px; background: var(--card); overflow: hidden;
  box-shadow: 0 1px 2px rgba(16,24,40,.04);
}
details.feature.passed { border-top-color: var(--passed); }
details.feature.failed { border-top-color: var(--failed); }
details.feature.skipped { border-top-color: var(--skipped); }
details.feature > summary {
  list-style: none; cursor: pointer; padding: 14px 18px; display: flex;
  align-items: center; gap: 12px; background: var(--bg-soft);
}
details.feature.passed > summary { background: linear-gradient(90deg, #eefdf3, var(--bg-soft) 70%); }
details.feature.failed > summary { background: linear-gradient(90deg, #fef2f2, var(--bg-soft) 70%); }
details.feature.skipped > summary { background: linear-gradient(90deg, #fffbeb, var(--bg-soft) 70%); }
details.feature > summary::-webkit-details-marker { display: none; }
details.feature > summary::before {
  content: "▸"; display: inline-block; transition: transform .15s ease; color: var(--text-muted);
}
details.feature[open] > summary::before { transform: rotate(90deg); }
.feature-name { font-weight: 700; font-size: 15px; }
.feature-meta { color: var(--text-muted); font-size: 12px; margin-left: auto; }
.feature-body { padding: 14px 18px; }

details.scenario {
  border: 1px solid var(--border); border-left: 4px solid var(--border);
  border-radius: 8px; margin-bottom: 10px; background: var(--card); overflow: hidden;
  transition: box-shadow .15s ease;
}
details.scenario:hover { box-shadow: 0 2px 10px rgba(16,24,40,.08); }
details.scenario.passed { border-left-color: var(--passed); }
details.scenario.failed { border-left-color: var(--failed); }
details.scenario.skipped { border-left-color: var(--skipped); }
details.scenario > summary {
  list-style: none; cursor: pointer; padding: 10px 14px; display: flex;
  align-items: center; gap: 10px; flex-wrap: wrap;
}
details.scenario.passed > summary { background: #f5fbf6; }
details.scenario.failed > summary { background: #fdf5f5; }
details.scenario.skipped > summary { background: #fffcf3; }
details.scenario > summary::-webkit-details-marker { display: none; }
details.scenario > summary::before {
  content: "▸"; display: inline-block; transition: transform .15s ease; color: var(--text-muted); font-size: 12px;
}
details.scenario[open] > summary::before { transform: rotate(90deg); }
.scenario-name { font-weight: 600; font-size: 13.5px; }
.scenario-meta { color: var(--text-muted); font-size: 12px; margin-left: auto; }
.scenario-body { padding: 4px 14px 14px 30px; background: var(--card); }

.scenario-error {
  background: #fff1f0; border: 1px solid #ffc1bc; border-radius: 6px;
  padding: 10px; margin: 4px 0 12px; font-size: 12px; white-space: pre-wrap;
  overflow-x: auto;
}

.step {
  border: 1px solid var(--border); border-left: 3px solid var(--border);
  border-radius: 8px; margin-bottom: 8px; overflow: hidden; transition: box-shadow .15s ease;
}
.step:hover { box-shadow: 0 2px 8px rgba(16,24,40,.08); }
.step.passed { border-left-color: var(--passed); }
.step.failed { border-left-color: var(--failed); border-color: #ffb3ac; }
.step-header {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  background: var(--bg-soft); font-size: 13px;
}
.step.passed .step-header { background: #f5fbf6; }
.step.failed .step-header { background: #fdf5f5; }
.step-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.step-dot.passed { background: linear-gradient(135deg, var(--passed-2), var(--passed)); }
.step-dot.failed { background: linear-gradient(135deg, var(--failed-2), var(--failed)); }
.step-keyword {
  font-weight: 700; font-size: 10.5px; text-transform: uppercase; letter-spacing: .03em;
  padding: 2px 8px; border-radius: 6px;
}
.step-name { font-weight: 500; }
.step-body { display: flex; gap: 14px; padding: 10px 12px; flex-wrap: wrap; align-items: flex-start; }
.step-logs { flex: 1 1 320px; min-width: 240px; }
.step-logs-label { font-size: 11px; font-weight: 700; color: var(--text-muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: .03em; }
.step-logs pre {
  margin: 0; background: var(--bg-soft); border: 1px solid var(--border); border-radius: 6px;
  padding: 8px 10px; font-size: 11.5px; line-height: 1.5; overflow-x: auto; max-height: 200px; overflow-y: auto;
}
.step-logs pre::-webkit-scrollbar { width: 6px; height: 6px; }
.step-logs pre::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
.step-logs pre::-webkit-scrollbar-thumb:hover { background: var(--accent-2); }
.step-error {
  background: #fff1f0; border: 1px solid #ffc1bc; border-radius: 6px;
  padding: 8px 10px; font-size: 11.5px; white-space: pre-wrap; margin-top: 8px; overflow-x: auto;
}
.no-logs { color: var(--text-muted); font-size: 12px; font-style: italic; }

.shot-thumb {
  flex: 0 0 auto; cursor: zoom-in; border: 1px solid var(--border); border-radius: 6px;
  overflow: hidden; width: 160px; height: 104px; position: relative; background: var(--bg-soft);
  transition: transform .15s ease, box-shadow .15s ease;
}
.shot-thumb:hover { transform: scale(1.04); box-shadow: 0 6px 16px rgba(16,24,40,.18); }
.shot-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.shot-thumb::after {
  content: "⤢"; position: absolute; top: 4px; right: 6px; color: #fff;
  text-shadow: 0 0 3px rgba(0,0,0,.7); font-size: 13px;
}

.lightbox {
  display: none; position: fixed; inset: 0; background: rgba(0,0,0,.85);
  z-index: 1000; align-items: center; justify-content: center;
}
.lightbox.open { display: flex; }
.lightbox img { max-width: 92vw; max-height: 88vh; border-radius: 8px; box-shadow: 0 10px 40px rgba(0,0,0,.6); }
.lightbox-close {
  position: absolute; top: 18px; right: 26px; background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.3); color: #fff; font-size: 22px; line-height: 1;
  width: 40px; height: 40px; border-radius: 50%; cursor: pointer; transition: background .15s ease, transform .15s ease;
}
.lightbox-close:hover { background: var(--failed); border-color: var(--failed); transform: scale(1.08); }

.empty-state {
  text-align: center; padding: 48px 20px; color: var(--text-muted); font-size: 14px;
  background: linear-gradient(180deg, #fff, var(--bg-soft)); border: 1px dashed var(--border); border-radius: 12px;
}
.empty-state::before {
  content: "🔍"; display: block; font-size: 26px; margin-bottom: 8px; opacity: .5;
}

mark {
  background: #ffe066; color: #1f2328; padding: 0 2px; border-radius: 3px; font-weight: 700;
}
"""

_SCRIPT = r"""
(function () {
  var overlay = document.getElementById('lightbox');
  var overlayImg = document.getElementById('lightbox-img');

  function openLightbox(src, alt) {
    overlayImg.src = src;
    overlayImg.alt = alt || '';
    overlay.classList.add('open');
  }

  function closeLightbox() {
    overlay.classList.remove('open');
    overlayImg.src = '';
  }

  document.addEventListener('click', function (e) {
    var thumb = e.target.closest('.shot-thumb');
    if (thumb) {
      var img = thumb.querySelector('img');
      openLightbox(img.src, img.alt);
      return;
    }
    if (e.target.id === 'lightbox' || e.target.id === 'lightbox-close') {
      closeLightbox();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeLightbox();
  });

  var currentFilter = 'all';
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));
  var searchInput = document.getElementById('search');
  var emptyState = document.getElementById('empty-state');
  var features = Array.prototype.slice.call(document.querySelectorAll('.feature'));
  var highlightTargets = Array.prototype.slice.call(
    document.querySelectorAll('.feature-name, .scenario-name, .step-name')
  );
  highlightTargets.forEach(function (el) { el.dataset.original = el.textContent; });

  function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function applyHighlight(term) {
    highlightTargets.forEach(function (el) {
      var original = el.dataset.original;
      if (!term) {
        el.textContent = original;
        return;
      }
      var re = new RegExp('(' + escapeRegExp(term) + ')', 'ig');
      el.innerHTML = escapeHtml(original).replace(re, '<mark>$1</mark>');
    });
  }

  function applyFilters() {
    var term = (searchInput.value || '').trim().toLowerCase();
    var narrowed = currentFilter !== 'all' || term !== '';
    var anyVisible = false;

    applyHighlight(term);

    features.forEach(function (featureEl) {
      var scenarios = Array.prototype.slice.call(featureEl.querySelectorAll('.scenario'));
      var featureHasVisible = false;

      scenarios.forEach(function (scEl) {
        var status = scEl.dataset.status;
        var searchable = scEl.dataset.search || '';
        var statusMatch = currentFilter === 'all' || status === currentFilter;
        var searchMatch = term === '' || searchable.indexOf(term) !== -1;
        var visible = statusMatch && searchMatch;

        scEl.style.display = visible ? '' : 'none';
        if (visible) {
          featureHasVisible = true;
          anyVisible = true;
          scEl.open = narrowed ? true : scEl.dataset.defaultOpen === 'true';
        }
      });

      featureEl.style.display = featureHasVisible ? '' : 'none';
    });

    emptyState.hidden = anyVisible;
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      currentFilter = tab.dataset.filter;
      applyFilters();
    });
  });

  searchInput.addEventListener('input', applyFilters);

  applyFilters();
})();
"""


_KEYWORD_COLORS = {
    "given": ("#eef2ff", "#4338ca"),
    "when": ("#fdf4ff", "#a21caf"),
    "then": ("#ecfdf5", "#047857"),
    "and": ("#f1f5f9", "#475569"),
    "but": ("#fff7ed", "#c2410c"),
}


def _rel(path: Path) -> str:
    return path.relative_to(REPORTS_DIR).as_posix()


def _render_step(step: StepResult) -> str:
    logs_html = (
        f"<pre>{escape(chr(10).join(step.logs))}</pre>"
        if step.logs
        else '<div class="no-logs">No log output for this step.</div>'
    )
    error_html = f'<div class="step-error">{escape(step.error)}</div>' if step.error else ""
    shot_html = (
        f'<div class="shot-thumb" title="Click to enlarge">'
        f'<img src="{_rel(step.screenshot)}" alt="{escape(step.keyword)} {escape(step.name)}" loading="lazy"></div>'
        if step.screenshot
        else ""
    )
    keyword = step.keyword.strip()
    kw_bg, kw_fg = _KEYWORD_COLORS.get(keyword.lower(), ("#f1f5f9", "#475569"))

    return f"""
        <div class="step {step.status}">
          <div class="step-header">
            <span class="step-dot {step.status}"></span>
            <span class="step-keyword" style="background:{kw_bg};color:{kw_fg};">{escape(keyword)}</span>
            <span class="step-name">{escape(step.name)}</span>
          </div>
          <div class="step-body">
            <div class="step-logs">
              <div class="step-logs-label">Log</div>
              {logs_html}
              {error_html}
            </div>
            {shot_html}
          </div>
        </div>
    """


def _render_scenario(scenario: ScenarioResult) -> str:
    steps_html = "".join(_render_step(s) for s in scenario.steps)
    error_html = (
        f'<div class="scenario-error">{escape(scenario.error)}</div>' if scenario.error else ""
    )
    default_open = scenario.status == "failed"

    search_terms = [scenario.name] + [f"{s.keyword} {s.name}" for s in scenario.steps]
    search_blob = escape(" ".join(search_terms).lower())

    return f"""
      <details class="scenario {scenario.status}" data-status="{scenario.status}"
                data-search="{search_blob}" data-default-open="{str(default_open).lower()}"
                {"open" if default_open else ""}>
        <summary>
          <span class="badge {scenario.status}">{scenario.status.upper()}</span>
          <span class="scenario-name">{escape(scenario.name)}</span>
          <span class="scenario-meta">{len(scenario.steps)} step(s) &middot; {scenario.duration:.2f}s</span>
        </summary>
        <div class="scenario-body">
          {error_html}
          {steps_html}
        </div>
      </details>
    """


def _render_feature(feature: FeatureResult) -> str:
    scenarios_html = "".join(_render_scenario(s) for s in feature.scenarios)
    return f"""
    <details class="feature" open>
      <summary>
        <span class="badge {feature.status}">{feature.status.upper()}</span>
        <span class="feature-name">{escape(feature.name)}</span>
        <span class="feature-meta">{escape(feature.filename)} &middot; {feature.passed_count}/{len(feature.scenarios)} passed</span>
      </summary>
      <div class="feature-body">
        {scenarios_html}
      </div>
    </details>
    """


def _pie_gradient(passed: int, failed: int, skipped: int, total: int) -> str:
    if total == 0:
        return "conic-gradient(var(--border) 0 100%)"
    passed_pct = passed / total * 100
    failed_pct = failed / total * 100
    p1 = passed_pct
    p2 = passed_pct + failed_pct
    return (
        f"conic-gradient(var(--passed) 0% {p1:.3f}%, "
        f"var(--failed) {p1:.3f}% {p2:.3f}%, "
        f"var(--skipped) {p2:.3f}% 100%)"
    )


def render_report(results: list[ScenarioResult], meta: RunMeta | None = None) -> str:
    meta = meta or RunMeta()
    total = len(results)
    passed = sum(1 for r in results if r.status == "passed")
    failed = sum(1 for r in results if r.status == "failed")
    skipped = total - passed - failed
    pass_pct = round(passed / total * 100) if total else 0
    fail_pct = round(failed / total * 100) if total else 0
    skip_pct = round(skipped / total * 100) if total else 0
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    features = _group_by_feature(results)
    body = "".join(_render_feature(f) for f in features) or ""

    pie_gradient = _pie_gradient(passed, failed, skipped, total)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Automation Test Run Report</title>
<style>{_STYLE}</style>
</head>
<body>
  <div class="page-header">
    <div class="inner">
      <h1>Automation Test Run Report</h1>
      <p class="subtitle">Generated {generated_at}</p>
    </div>
  </div>

  <div class="page">
    <div class="overview">
      <div class="meta-section">
        <h2>Run Details</h2>
        <div class="stat-grid">
          <div class="stat-card stat-c1"><div class="stat-label">Browser</div><div class="stat-value">{escape(meta.browser_name)}</div></div>
          <div class="stat-card stat-c2"><div class="stat-label">Browser Version</div><div class="stat-value">{escape(meta.browser_version)}</div></div>
          <div class="stat-card stat-c3"><div class="stat-label">Playwright Version</div><div class="stat-value">{escape(meta.playwright_version)}</div></div>
          <div class="stat-card stat-c4"><div class="stat-label">Python Version</div><div class="stat-value">{escape(meta.python_version)}</div></div>
          <div class="stat-card stat-c5"><div class="stat-label">Start Time</div><div class="stat-value">{escape(meta.start_display)}</div></div>
          <div class="stat-card stat-c6"><div class="stat-label">End Time</div><div class="stat-value">{escape(meta.end_display)}</div></div>
          <div class="stat-card stat-c7"><div class="stat-label">Total Execution Time</div><div class="stat-value">{escape(meta.duration_display)}</div></div>
          <div class="stat-card stat-c8"><div class="stat-label">Total Tests</div><div class="stat-value">{total}</div></div>
        </div>
      </div>

      <div class="card chart-card">
        <h2>Pass / Fail Ratio</h2>
        <div class="chart-wrap">
          <div class="pie" style="--pie-bg: {pie_gradient};">
            <div class="pie-center">
              <strong>{pass_pct}%</strong>
              <span>passed</span>
            </div>
          </div>
          <ul class="legend">
            <li><span class="dot passed"></span>Passed <b>{passed}</b><span class="pct">({pass_pct}%)</span></li>
            <li><span class="dot failed"></span>Failed <b>{failed}</b><span class="pct">({fail_pct}%)</span></li>
            <li><span class="dot skipped"></span>Skipped <b>{skipped}</b><span class="pct">({skip_pct}%)</span></li>
          </ul>
        </div>
      </div>
    </div>

    <div class="controls">
      <div class="tabs">
        <button class="tab active" data-filter="all">All Tests <span class="count">{total}</span></button>
        <button class="tab" data-filter="passed">Passed <span class="count">{passed}</span></button>
        <button class="tab" data-filter="failed">Failed <span class="count">{failed}</span></button>
      </div>
      <div class="search-wrap">
        <input id="search" type="search" placeholder="Search scenarios or steps...">
      </div>
    </div>

    <div id="results">
      {body}
    </div>
    <div id="empty-state" class="empty-state" hidden>No tests match the current filter / search.</div>
  </div>

  <div id="lightbox" class="lightbox">
    <button id="lightbox-close" class="lightbox-close" aria-label="Close">&times;</button>
    <img id="lightbox-img" src="" alt="">
  </div>

  <script>{_SCRIPT}</script>
</body>
</html>
"""


def write_report(results: list[ScenarioResult], meta: RunMeta | None = None) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(render_report(results, meta), encoding="utf-8")
    return REPORT_FILE



def write_results_json(results: list[ScenarioResult]) -> Path:
    """Machine-readable failures for ci/analyze_failures.py (failed step, error, screenshot)."""
    failed = []
    for r in results:
        if r.status != "failed":
            continue
        step = next((st for st in r.steps if st.status == "failed"), None)
        failed.append(
            {
                "scenario": r.name,
                "feature": r.feature_name,
                "feature_file": r.feature_file,
                "failed_step": f"{step.keyword} {step.name}".strip() if step else None,
                "step_error": (step.error if step else r.error) or "",
                "step_logs": step.logs[-10:] if step else [],
                "screenshot": _rel(step.screenshot) if step and step.screenshot else None,
                "steps_passed_before": sum(1 for st in r.steps if st.status == "passed"),
            }
        )
    path = REPORTS_DIR / "results.json"
    path.write_text(json.dumps({"failed": failed}, indent=2), encoding="utf-8")
    return path
