#!/usr/bin/env bash
set -ex
rustc -V
cargo -V

if [ $(uname) = Darwin ] ; then
  export RUSTFLAGS="-C link-args=-Wl,-rpath,${PREFIX}/lib"
else
  export RUSTFLAGS="-C link-args=-Wl,-rpath-link,${PREFIX}/lib"
fi

cd testing/geckodriver
cargo build --release --verbose
cargo install --root "${PREFIX}" --path .

rm -f "${PREFIX}/.crates.toml"
