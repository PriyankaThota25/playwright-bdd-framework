from __future__ import annotations

import os
import platform
from datetime import datetime
from importlib.metadata import version as pkg_version

import pytest
from playwright.sync_api import sync_playwright

from config.settings import Settings, get_settings
from core.browser_factory import launch_browser, new_context
from core.logger import get_logger, step_log_capture
from core.report import RunMeta, ScenarioResult, StepResult, write_report, write_results_json
from core.screenshot import ScenarioScreenshots

logger = get_logger(__name__)

_scenario_results: list[ScenarioResult] = []
_run_meta = RunMeta(
    python_version=platform.python_version(),
    playwright_version=pkg_version("playwright"),
)


def pytest_sessionstart(session: pytest.Session) -> None:
    _run_meta.start_time = datetime.now()


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--feature-file",
        action="store",
        default=None,
        help="Only run scenarios defined in this .feature file, e.g. --feature-file=login.feature",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    feature_name = config.getoption("--feature-file")
    if not feature_name:
        return

    selected, deselected = [], []
    for item in items:
        scenario = getattr(item.obj, "__scenario__", None)
        filename = os.path.basename(scenario.feature.filename) if scenario else None
        (selected if filename == feature_name else deselected).append(item)

    config.hook.pytest_deselected(items=deselected)
    items[:] = selected


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, settings: Settings):
    browser = launch_browser(playwright_instance, settings)
    _run_meta.browser_name = settings.browser
    _run_meta.browser_version = browser.version
    logger.info("Launched %s (headless=%s)", settings.browser, settings.headless)
    yield browser
    browser.close()


@pytest.fixture
def context(browser, settings: Settings):
    ctx = new_context(browser, settings)
    yield ctx
    ctx.close()


@pytest.fixture
def page(context):
    pg = context.new_page()
    yield pg


def pytest_bdd_before_scenario(request: pytest.FixtureRequest, feature, scenario) -> None:
    request.node._screenshots = ScenarioScreenshots(scenario.name)
    request.node._report_scenario = ScenarioResult(
        name=scenario.name,
        feature_name=feature.name or os.path.basename(feature.filename),
        feature_file=os.path.basename(feature.filename),
    )
    step_log_capture.drain()  # discard any noise logged before the first step


def pytest_bdd_before_step(
    request: pytest.FixtureRequest, feature, scenario, step, step_func
) -> None:
    step_log_capture.drain()  # start this step with a clean log buffer


def pytest_bdd_after_step(
    request: pytest.FixtureRequest, feature, scenario, step, step_func, step_func_args
) -> None:
    result: ScenarioResult | None = getattr(request.node, "_report_scenario", None)
    screenshots: ScenarioScreenshots | None = getattr(request.node, "_screenshots", None)
    logs = step_log_capture.drain()
    if result is None or screenshots is None:
        return
    page = request.getfixturevalue("page")
    path = screenshots.capture(page)
    result.steps.append(
        StepResult(keyword=step.keyword, name=step.name, status="passed", logs=logs, screenshot=path)
    )


def pytest_bdd_step_error(
    request: pytest.FixtureRequest,
    feature,
    scenario,
    step,
    step_func,
    step_func_args,
    exception,
) -> None:
    result: ScenarioResult | None = getattr(request.node, "_report_scenario", None)
    screenshots: ScenarioScreenshots | None = getattr(request.node, "_screenshots", None)
    logs = step_log_capture.drain()
    if result is None or screenshots is None:
        return
    page = request.getfixturevalue("page")
    path = screenshots.capture(page, failed=True)
    result.steps.append(
        StepResult(
            keyword=step.keyword,
            name=step.name,
            status="failed",
            logs=logs,
            screenshot=path,
            error=str(exception),
        )
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()

    # A scenario contributes one result: from the "call" phase normally, or
    # from "setup" if a fixture failed before any step could run.
    if report.when != "call" and not (report.when == "setup" and report.failed):
        return

    result: ScenarioResult | None = getattr(item, "_report_scenario", None)
    if result is None:
        return

    result.status = "passed" if report.passed else "failed" if report.failed else "skipped"
    result.duration = report.duration
    if report.failed and not result.steps:
        result.error = str(report.longrepr)

    _scenario_results.append(result)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    _run_meta.end_time = datetime.now()
    path = write_report(_scenario_results, _run_meta)
    logger.info("Wrote test report -> %s", path)
    write_results_json(_scenario_results)