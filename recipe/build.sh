#!/usr/bin/env bash
# NOTE: mostly derived from
# https://github.com/conda-forge/py-spy-feedstock/blob/master/recipe/build.sh

set -o xtrace -o nounset -o pipefail -o errexit

export RUST_BACKTRACE=1

if [ $(uname) = Darwin ] ; then
  export RUSTFLAGS="-C link-args=-Wl,-rpath,${PREFIX}/lib"
else
  export RUSTFLAGS="-C link-arg=-Wl,-rpath-link,${PREFIX}/lib -L${PREFIX}/lib"
fi

# dump licenses
cargo-bundle-licenses --format yaml --output THIRDPARTY.yml

# build statically linked binary with Rust
cargo install --locked --root "$PREFIX" --path .

# remove extra build files
rm -f "${PREFIX}/.crates2.json"
rm -f "${PREFIX}/.crates.toml"
