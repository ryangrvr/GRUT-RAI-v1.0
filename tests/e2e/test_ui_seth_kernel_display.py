import subprocess
import time
import urllib.request
import signal
import os
import pytest

# Skip E2E tests unless Playwright is installed (dev-only)
pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

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
    p = subprocess.Popen(["python", "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", f"--port", str(PORT)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        wait_for_health(SERVER_URL + "/health", timeout_s=20)
    except Exception:
        p.terminate()
        p.wait(timeout=5)
        raise
    return p


def test_ui_shows_seth_kernel_and_result_meta():
    proc = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(SERVER_URL + "/ui")

            # Open the Anamnesis tab
            page.click('#tabAnam')

            # Run the demo
            page.click('button:has-text("Run Demo")')

            # Wait for demo result to appear and include kernel info
            page.wait_for_selector('#anamResContainer', timeout=10000)
            page.wait_for_function("() => document.querySelector('#demoRes') && document.querySelector('#demoRes').innerText.includes('Kernel')", timeout=10000)

            # Assert kernel name is displayed as Seth Kernel
            demo_text = page.inner_text('#demoRes')
            assert 'Seth Kernel' in demo_text

            # Assert standardized result header shows a status badge and short hashes
            page.wait_for_function("() => document.getElementById('resultStatusBadge') && document.getElementById('resultStatusBadge').textContent.trim() !== '—'", timeout=10000)
            status = page.inner_text('#resultStatusBadge').strip()
            assert status != '—'

            params_short = page.inner_text('#paramsHash').strip()
            bundle_short = page.inner_text('#bundleHash').strip()
            assert params_short != '—' and len(params_short) >= 4
            assert bundle_short != '—' and len(bundle_short) >= 4

            # Export button should be visible for a completed run
            assert page.is_visible('#exportBtn')

            browser.close()
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
            proc.wait()
