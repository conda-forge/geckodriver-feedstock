""" test whether firefox is viable with geckodriver and selenium

    Adapted from (and should be kept in sync with)
    https://github.com/conda-forge/firefox-feedstock/blob/master/recipe/test_selenium.py
"""
import sys
import os
import re

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import pytest

LICENSE_CANARY = re.escape("Mozilla Public License 2.0")
SUPPORT_CANARY = r"""<td id="application-box">\s*?Firefox\s*?</td>"""

if os.environ["PKG_NAME"] == "firefox":
    SUPPORT_CANARY = (
        r"""<td id="version-box">\s*"""
        f"""{re.escape(os.environ["PKG_VERSION"])}"""
        r"""\s*</td>"""
    )


@pytest.fixture
def binary_paths():
    plat = sys.platform.lower()
    if "win32" in plat:
        firefox = Path(os.environ["LIBRARY_BIN"]) / "firefox.exe"
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


@pytest.fixture
def driver(tmp_path, binary_paths):
    log = tmp_path / "geckodriver.log"

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(
        options=options,
        service_log_path=str(log),
        service_args=["--log", "trace"],
        **binary_paths,
    )

    yield driver
    driver.quit()

    print(
        "BEGIN geckodriver.log\n\n"
        f"""{log.read_text(encoding="utf-8")}"""
        "\n\nEND geckdriver.log"
    )


@pytest.mark.parametrize(
    "thing,url,expected_re",
    [
        ["license", "about:license", LICENSE_CANARY],
        ["support", "about:support", SUPPORT_CANARY],
    ],
)
def test_page(thing, url, expected_re, tmp_path, driver):
    html = tmp_path / f"{thing}.html"
    png = tmp_path / f"{thing}.png"

    print(f"checking {url} for `{expected_re}`...")
    driver.get(url)
    source = driver.page_source

    assert re.findall(expected_re, source)

    html.write_text(driver.page_source)

    driver.save_screenshot(str(png))

    # TODO: pdf
