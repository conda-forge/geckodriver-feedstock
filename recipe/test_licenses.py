""" Verify that geckodriver dependency licenses are present.

    mostly copied from:
    https://github.com/conda-forge/pysyntect-feedstock/blob/master/recipe/check_licenses.py

    If this fails, you'll probably need to:
    - ensure the magic-named file(s) exist in library_licenses
    - ensure the magic-named file is included in meta.yaml#/license_file
"""
import json
import os
import sys
import subprocess
from pathlib import Path

import ruamel_yaml
import pytest

# first-party crates my be covered by packaged LICENSE-* file
IGNORE = {}

# convenience for local testing
DEPENDENCIES_JSON = os.environ.get("DEPENDENCIES_JSON")

# paths unlikely to change per package
CARGO_HOME = Path(os.environ["CARGO_HOME"])
RECIPE_DIR = Path(os.environ["RECIPE_DIR"])
SRC_DIR = Path(os.environ["SRC_DIR"])

# probably will change per recipe
CARGO_TOML = SRC_DIR / "testing" / "geckodriver" / "Cargo.toml"
LIBRARY_LICENSES = RECIPE_DIR / "library_licenses"
LICENSE_FILE_NAMES = sorted([f.name for f in LIBRARY_LICENSES.glob("*")])

# TODO: https://github.com/conda-forge/staged-recipes/issues/12278
CARGO_LICENSES_BIN = CARGO_HOME / "bin" / "cargo-license"


def _load_dependencies():
    if DEPENDENCIES_JSON is not None:
        dependencies = json.loads(Path(DEPENDENCIES_JSON).read_text(encoding="utf-8"))
    else:
        assert CARGO_TOML.exists()
        out = subprocess.check_output(
            [str(CARGO_LICENSES_BIN), "--json"],
            cwd=str(CARGO_TOML.parent)
        )
        dependencies = json.loads(out.decode("utf-8"))

    print(
        "raw dependencies",
        json.dumps(dependencies, indent=2, sort_keys=True),
        flush=True
    )

    return {
        crate["name"]: crate for crate in dependencies
        if crate["name"] not in IGNORE
    }

DEPENDENCIES = _load_dependencies()


@pytest.fixture(params=DEPENDENCIES.keys())
def crate(request):
    return request.param

def _yaml_licenses():
    return list(ruamel_yaml.safe_load(
        (RECIPE_DIR / "meta.yaml")
        .read_text("utf-8")
        .split("# BEGIN license_file")[1]
        .split("# END license_file")[0]
    ))


@pytest.fixture
def yaml_licenses():
    return _yaml_licenses()


def test_missing_license(crate, yaml_licenses):
    """ looks for magic-named files
        handles at least:

        library_licenses/<crate-name>-LICEN(S|C)E-(|-MIT|-APACHE|-ZLIB)

        COPYING is not a license, but some of the manually-built files need it
        for clarification
    """
    assert LIBRARY_LICENSES.exists()
    matches = list(LIBRARY_LICENSES.glob(f"{crate}-LICEN*"))

    errors = []

    if not matches:
        errors += ["no license files"]

    for match in matches:
        if f"library_licenses/{match.name}" not in yaml_licenses:
            errors += ["not in meta.yaml"]

    assert not errors, DEPENDENCIES[crate]


@pytest.mark.parametrize("license_file_name", LICENSE_FILE_NAMES)
def test_over_licensed(license_file_name):
    if "-LICENSE" in license_file_name:
        crate = license_file_name.split("-LICENSE")[0]
    elif "-COPYING" in license_file_name:
        crate = license_file_name.split("-COPYING")[0]
    else:
        return

    assert crate in DEPENDENCIES, f"not a dependency"


@pytest.mark.parametrize("license_file", LICENSE_FILE_NAMES)
def test_license_not_in_yaml(license_file, yaml_licenses):
    assert f"library_licenses/{license_file}" in yaml_licenses


@pytest.mark.parametrize("license_in_yaml", _yaml_licenses())
def test_yaml_license_missing(license_in_yaml):
    assert license_in_yaml.split("/")[1] in LICENSE_FILE_NAMES
