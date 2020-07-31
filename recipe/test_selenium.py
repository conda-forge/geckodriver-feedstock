""" test whether firefox is viable with geckodriver and selenium

    Adapted from
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


@pytest.fixture
def binary_paths():
    plat = sys.platform.lower()
    if "win32" in plat:
        firefox = Path(os.environ["LIBRARY_BIN"]) / "firefox.exe",
        geckodriver = Path(os.environ["SCRIPTS"]) / "geckodriver.exe"
    else:
        geckodriver = Path(sys.prefix) / "bin" / "geckodriver"
        app_dir = Path(sys.prefix) / "bin" / "FirefoxApp"

        if "linux" in plat:
            firefox = app_dir / "firefox"
        else:
            firefox = app_dir / "Contents" / "MacOS" / "firefox"

    assert firefox.exists()
    assert geckodriver.exists()

    return dict(
        firefox_binary=str(firefox),
        executable_path=str(geckodriver),
    )


def test_read_license(tmp_path, binary_paths):
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
            service_log_path=str(geckodriver_log),
            service_args=["--log", "trace"],
            **binary_paths,
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
            print(log.read_text(encoding="utf-8"))
        else:
            yield f"... {log.name} was NOT created!"
        print(f"... end {log.name} check")
