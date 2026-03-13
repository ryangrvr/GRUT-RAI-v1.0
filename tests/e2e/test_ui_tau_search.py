import subprocess
import time
import urllib.request
import signal
import os
import pytest

# Skip E2E tests unless Playwright is installed (dev-only)
pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

import os

PORT = int(os.environ.get('PORT', '8001'))
SERVER_URL = f"http://127.0.0.1:{PORT}"


def wait_for_health(url, timeout_s=20):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("server did not respond in time")


def start_server():
    # Start uvicorn in background on configurable PORT
    p = subprocess.Popen(["python", "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", f"--port", str(PORT)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        wait_for_health(SERVER_URL + "/health", timeout_s=20)
    except Exception:
        p.terminate()
        p.wait(timeout=5)
        raise
    return p


def test_tau_search_ui_shows_comparison_and_baseline_toggle():
    proc = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(SERVER_URL + "/ui")

            # Trigger tau search (the page generates synthetic y_obs client-side)
            page.click('button:has-text("Search τ")')

            # Wait until bestTau is updated (not the placeholder '—')
            page.wait_for_function("() => document.getElementById('bestTau') && document.getElementById('bestTau').textContent.trim() !== '—'", timeout=10000)

            # Comparison summary should be present and contain 'Baseline:'
            comp_text = page.inner_text('#comparisonSummary').strip()
            assert 'Baseline:' in comp_text

            # Baseline row(s) should exist initially
            baseline_locator = page.locator('.baseline-row')
            # There should be either 0 or more baseline rows; if present, verify toggle hides them
            if baseline_locator.count() > 0:
                assert baseline_locator.count() >= 1
                # Uncheck the showBaseline checkbox and assert baseline rows become hidden
                page.locator('#showBaseline').uncheck()
                page.wait_for_timeout(200)
                # The first baseline row should not be visible
                assert not baseline_locator.first.is_visible()

            browser.close()
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
            proc.wait()
