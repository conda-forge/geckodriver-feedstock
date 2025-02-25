#!/usr/bin/env bash
# NOTE: mostly derived from
# https://github.com/conda-forge/py-spy-feedstock/blob/master/recipe/build.sh

set -o xtrace -o nounset -o pipefail -o errexit

export RUST_BACKTRACE=1

export CARGO_PROFILE_RELEASE_STRIP=symbols

_UNAME="$(uname)"

if [[ "${_UNAME}" = Darwin ]] ; then
  export RUSTFLAGS="-C link-args=-Wl,-rpath,${PREFIX}/lib"
else
  export RUSTFLAGS="-C link-arg=-Wl,-rpath-link,${PREFIX}/lib -L${PREFIX}/lib"
fi

unzip license.zip
unzip -q testing.zip

cd mozilla-central-*

cp toolkit/content/license.html "${SRC_DIR}"

cd testing/geckodriver

# build statically linked binary with Rust
cargo install \
  --no-track \
  --locked \
  --path . \
  --profile release \
  --root "${PREFIX}"

cargo-bundle-licenses \
  --format yaml \
  --output "${SRC_DIR}/THIRDPARTY.yml"
