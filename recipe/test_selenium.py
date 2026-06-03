"""test whether firefox is viable with geckodriver and selenium

Adapted from
https://github.com/conda-forge/firefox-feedstock/blob/master/recipe/run_test.py
"""

from __future__ import annotations
import sys
import os
import re
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from textwrap import indent

import pytest

LICENSE_CANARY = re.escape("Mozilla Public License 2.0")
SUPPORT_CANARY = r"""<td id="application-box">\s*?Firefox\s*?</td>"""

if os.environ["PKG_NAME"] == "firefox":
    SUPPORT_CANARY = (
        r"""<td id="version-box">\s*"""
        f"""{re.escape(os.environ["PKG_VERSION"])}"""
        r"""\s*</td>"""
    )

os.environ.update(MOZ_HEADLESS="1")


@pytest.fixture
def binary_paths() -> tuple[Path, Path]:
    plat = sys.platform.lower()
    if "win32" in plat:
        firefox = Path(os.environ["LIBRARY_BIN"]) / "firefox.exe"
        geckodriver = Path(os.environ["SCRIPTS"]) / "geckodriver.exe"
    else:
        geckodriver = Path(sys.prefix) / "bin/geckodriver"
        app_dir = Path(sys.prefix) / "bin/FirefoxApp"

        if "linux" in plat:
            firefox = app_dir / "firefox"
        else:
            firefox = app_dir / "Contents/MacOS/firefox"

    assert firefox.exists()
    assert geckodriver.exists()

    return firefox, geckodriver


@pytest.fixture
def driver(tmp_path: Path, binary_paths: tuple[Path, Path]) -> webdriver.Firefox:
    firefox, geckodriver = binary_paths
    log = tmp_path / "geckodriver.log"

    options = Options()
    options.binary_location = str(firefox)

    service = Service(
        executable_path=str(geckodriver),
        service_args=["--log", "trace"],
        # https://github.com/SeleniumHQ/seleniumhq.github.io/commit/c11605ec062e49b2cbf1a35ddca0bf78224cc75f
        log_path=str(log),
        log_output=str(log),
    )

    driver = webdriver.Firefox(options=options, service=service)

    yield driver

    driver.quit()

    print(
        "BEGIN geckodriver.log\n\n"
        f"""{indent(log.read_text(encoding="utf-8"), "\t")}"""
        "\n\nEND geckdriver.log"
    )


@pytest.mark.parametrize(
    "thing,url,expected_re",
    [
        ["license", "about:license", LICENSE_CANARY],
        ["support", "about:support", SUPPORT_CANARY],
    ],
)
def test_page(
    thing: str, url: str, expected_re: str, tmp_path: Path, driver: webdriver.Firefox
) -> None:
    html = tmp_path / f"{thing}.html"
    png = tmp_path / f"{thing}.png"

    print(f"checking {url} for `{expected_re}`...")
    driver.get(url)

    for i in range(3):
        source = driver.page_source
        matches = [*re.findall(expected_re, source)]
        if matches:
            break
        time.sleep(3)

    assert matches, f"couldn't find {expected_re} in {url}, {source}"

    html.write_text(source)

    driver.save_screenshot(str(png))

    # TODO: pdf
