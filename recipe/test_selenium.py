""" test whether firefox is viable with geckodriver and selenium

    Adaptes from
    https://github.com/conda-forge/firefox-feedstock/blob/master/recipe/run_test.py
"""
import sys
import os
import subprocess
import traceback
import json

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import pytest

# on the old CI images, glibc is too old
# IGNORE_FIREFOX_FAIL = "linux" in sys.platform.lower()
IGNORE_FIREFOX_FAIL = False

if "IGNORE_FIREFOX_FAIL" in os.environ:
    IGNORE_FIREFOX_FAIL = json.loads(os.environ["IGNORE_FIREFOX_FAIL"])

# bin/firefox is a wrapper script
FIREFOX = Path(sys.prefix) / "bin" / "FirefoxApp" / "firefox"
GECKODRIVER = Path(sys.prefix) / "bin" / "geckodriver"


if "win32" in sys.platform.lower():
    FIREFOX = Path(os.environ["LIBRARY_BIN"]) / "firefox.exe"
    GECKODRIVER = Path(os.environ["SCRIPTS"]) / "geckodriver.exe"


@pytest.mark.parametrize("path,expected_version,ignore_fail", [
    [FIREFOX, None, IGNORE_FIREFOX_FAIL],
    [GECKODRIVER, os.environ["PKG_VERSION"], False]
])
def test_binary_version(path, expected_version, ignore_fail):
    """ assert that the path exists, is callable, and maybe has the right version
    """
    assert path.exists(), "binary not found"

    version = ""
    subprocess.call([str(path), "--version"])
    proc = subprocess.Popen([str(path), "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    for pipe in [stdout, stderr]:
        version += pipe.decode("utf-8") if pipe else ""

    assert ignore_fail or version.strip(), "no output received"

    if expected_version:
        assert ignore_fail or expected_version in version

def test_read_license(tmp_path):
    geckodriver_log = tmp_path / "geckodriver.log"
    html_log = tmp_path / "license.html"
    license_png = tmp_path / "license.png"

    print("testing about:license with selenium...")
    driver = None
    errors = []
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(
            options=options,
            firefox_binary=str(FIREFOX),
            executable_path=str(GECKODRIVER),
            service_log_path=str(geckodriver_log),
            service_args=["--log", "trace"]
        )
        driver.get("about:license")

        if driver.page_source:
            html_log.write_text(driver.page_source)
            assert "Mozilla Public License 2.0" in driver.page_source, \
                "couldn't even load the license page"
            driver.save_screenshot(str(license_png))
            assert license_png.exists()
    except Exception as err:
        print(f"\nEncountered unexpected error: {type(err)} {err}...\n")
        print(traceback.format_exc())
        if not IGNORE_FIREFOX_FAIL:
            errors += [err]
            raise Exception("license check failed") from err
    finally:
        errors += list(_dump_logs([geckodriver_log]))

        if driver:
            driver.quit()

        assert not errors


def _dump_logs(logs):
    for log in logs:
        print(f"Checking {log.name}...\n")
        if log.exists():
            print(log.read_text())
        else:
            yield f"... {log.name} was NOT created!"
        print(f"... end {log.name} check")
