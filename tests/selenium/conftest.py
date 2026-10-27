"""
conftest.py - Pytest fixtures and test environment configuration for Selenium WebDriver.
Configures headless Chrome, explicit wait helpers, an isolated test SQLite database,
and automatically starts the local Flask application server if not already running.
"""

import os
import sys
import time
import socket
import threading
import urllib.request
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Configure isolated test database path
TEST_DB_PATH = os.path.join(PROJECT_ROOT, "test_selenium.db")
os.environ["DATABASE_PATH"] = TEST_DB_PATH

# Directory for genuine test execution screenshots
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "test_artifacts", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

REPORTS_DIR = os.path.join(PROJECT_ROOT, "test_artifacts", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def is_port_open(host: str, port: int) -> bool:
    """Checks whether the given TCP port is currently listening."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        res = s.connect_ex((host, port))
        return res == 0
    finally:
        s.close()


def wait_for_server(url: str, timeout: float = 6.0) -> bool:
    """Polls a URL until it returns HTTP 200 or timeout occurs."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.15)
    return False


@pytest.fixture(scope="session")
def test_db():
    """Initializes and seeds an isolated test SQLite database before the test session."""
    from database import init_db
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass
    init_db(TEST_DB_PATH)
    yield TEST_DB_PATH


@pytest.fixture(scope="session")
def base_url(test_db):
    """
    Ensures the Flask web application is running and accessible.
    If the application is already running on port 5000, connects to it.
    Otherwise, starts the Flask app in a daemon background thread.
    """
    host = "127.0.0.1"
    port = 5000
    target_url = f"http://{host}:{port}"

    if not is_port_open(host, port):
        # Start Flask in background thread
        from app import app
        app.config["TESTING"] = True
        app.config["DEBUG"] = False

        # Run with werkzeug server in daemon thread
        server_thread = threading.Thread(
            target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
            daemon=True
        )
        server_thread.start()

        if not wait_for_server(target_url, timeout=8.0):
            raise RuntimeError(f"Could not connect to Flask application at {target_url} within timeout.")

    return target_url


@pytest.fixture(scope="session")
def driver():
    """
    Instantiates and configures a Selenium Chrome WebDriver instance in headless mode.
    Session-scoped for rapid, deterministic test execution across all test cases.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-search-engine-choice-screen")

    driver_instance = webdriver.Chrome(options=chrome_options)
    driver_instance.set_page_load_timeout(15)

    yield driver_instance

    try:
        driver_instance.quit()
    except Exception:
        pass


@pytest.fixture
def capture_screenshot():
    """Fixture providing a helper function to save genuine screenshots with timestamp and verification."""
    def _capture(driver_instance, filename: str) -> str:
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        driver_instance.save_screenshot(filepath)
        assert os.path.exists(filepath), f"Screenshot was not created: {filepath}"
        assert os.path.getsize(filepath) > 0, f"Screenshot file is empty: {filepath}"
        return filepath
    return _capture


@pytest.fixture
def wait_helper():
    """Fixture providing an explicit wait helper with standard timeout."""
    def _wait(driver_instance, timeout: float = 8.0):
        return WebDriverWait(driver_instance, timeout)
    return _wait
