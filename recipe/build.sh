#!/usr/bin/env bash
set -ex
rustc -V
cargo -V

export CARGO_HOME="$BUILD_PREFIX/cargo"
mkdir $CARGO_HOME

if [ $(uname) = Darwin ] ; then
  export RUSTFLAGS="-C link-args=-Wl,-rpath,${PREFIX}/lib"
else
  export RUSTFLAGS="-C link-args=-Wl,-rpath-link,${PREFIX}/lib"
fi

# Install cargo-license
cargo install cargo-license

# this is a little awkward, but saves the lengthy build
pushd $RECIPE_DIR
pytest -svv test_licenses.py
popd

cd testing/geckodriver

cargo build --release --verbose
cargo install --root "${PREFIX}" --path .

rm -f "${PREFIX}/.crates.toml"
