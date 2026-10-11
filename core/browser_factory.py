from __future__ import annotations

from playwright.sync_api import Browser, BrowserContext, Playwright

from config.settings import Settings

_LAUNCHERS = {
    "chromium": lambda pw: pw.chromium,
    "firefox": lambda pw: pw.firefox,
    "webkit": lambda pw: pw.webkit,
}


def launch_browser(playwright: Playwright, settings: Settings) -> Browser:
    try:
        browser_type = _LAUNCHERS[settings.browser]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported browser '{settings.browser}'. Use one of {list(_LAUNCHERS)}"
        ) from exc

    return browser_type(playwright).launch(
        headless=settings.headless,
        slow_mo=settings.slow_mo,
    )


def new_context(browser: Browser, settings: Settings) -> BrowserContext:
    context = browser.new_context(
        base_url=settings.base_url,
        viewport={"width": settings.viewport.width, "height": settings.viewport.height},
    )
    context.set_default_timeout(settings.timeout)
    context.set_default_navigation_timeout(settings.navigation_timeout)
    return context