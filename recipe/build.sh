#!/usr/bin/env bash
set -ex
rustc -V
cargo -V

if [ $(uname) = Darwin ] ; then
  export RUSTFLAGS="-C link-args=-Wl,-rpath,${PREFIX}/lib"
else
  export RUSTFLAGS="-C link-args=-Wl,-rpath-link,${PREFIX}/lib"
fi

# Install cargo-license
export CARGO_HOME="$BUILD_PREFIX/cargo"
mkdir $CARGO_HOME
cargo install cargo-license

# Check that all downstream libraries licenses are present
export PATH=$PATH:$CARGO_HOME/bins
cargo-license --json > dependencies.json
cat dependencies.json

python $RECIPE_DIR/check_licenses.py

cd testing/geckodriver
cargo build --release --verbose
cargo install --root "${PREFIX}" --path .

rm -f "${PREFIX}/.crates.toml"
