import os
import subprocess
import time
import urllib.request
import json
import signal
import urllib.parse
import pytest

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


def test_publish_and_open_snapshot():
    # Skip if Playwright not installed (dev-only)
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    proc = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(SERVER_URL + "/ui")

            # Go to Library tab and refresh
            page.click('[data-testid="tab-library"]')
            page.click('[data-testid="library-refresh"]')

            # If no publish buttons, create a demo run via the UI
            if page.locator('[data-testid^="run-publish-"]').count() == 0:
                # Run demo from reconstruction panel
                page.click('button:has-text("Run Demo")')
                # Wait a moment for run to be created and captured
                page.wait_for_timeout(500)
                page.click('[data-testid="library-refresh"]')

            # Wait for at least one publish button to appear
            page.wait_for_selector('[data-testid^="run-publish-"]', timeout=5000)

            # Click the first publish button (handle alert)
            published_slug = None
            def on_dialog(dialog):
                nonlocal published_slug
                text = dialog.message
                dialog.accept()
                # try to parse slug from message, look for '/p/' occurrence
                if '/p/' in text:
                    parsed = text.split('/p/')[-1].strip()
                    # strip any trailing characters
                    published_slug = parsed.split()[0]

            page.on('dialog', lambda dialog: on_dialog(dialog))
            first_pub = page.locator('[data-testid^="run-publish-"]').first
            first_pub.click()

            # Wait for the published button to appear for that run
            page.wait_for_selector('[data-testid^="run-published-"]', timeout=5000)

            # Click the published button to open modal
            page.locator('[data-testid^="run-published-"]').first.click()
            page.wait_for_selector('[data-testid="published-modal"]', timeout=5000)

            # Get the published link href from modal
            href = page.locator('[data-testid="published-link"]').get_attribute('href')
            assert href is not None
            # Normalize slug
            slug = href.split('/p/')[-1]

            # Fetch /p/{slug}/info to get full evidence packet
            info_url = SERVER_URL + f"/p/{slug}/info"
            with urllib.request.urlopen(info_url) as resp:
                assert resp.status == 200
                info_obj = json.load(resp)

            assert 'evidence_packet' in info_obj
            packet = info_obj['evidence_packet']
            assert packet.get('schema') == 'grut-evidence-v1'
            header = packet.get('header', {})
            for key in ('kind','engine_version','params_hash','status','bundle_hash'):
                assert key in header
            assert 'request' in packet and 'response' in packet
            assert 'receipt' in packet and 'status' in packet['receipt']

            # Also check the sanitized public view and revision endpoint
            with urllib.request.urlopen(SERVER_URL + f"/p/{slug}") as resp2:
                pub_view = json.load(resp2)
                assert 'header' in pub_view
            rev = info_obj.get('revision', 1)
            with urllib.request.urlopen(SERVER_URL + f"/p/{slug}/{rev}") as resp3:
                rev_view = json.load(resp3)
                assert 'header' in rev_view

            browser.close()
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
            proc.wait()
