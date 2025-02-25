@echo on
set CARGO_PROFILE_RELEASE_STRIP=symbols

unzip license.zip
unzip -q testing.zip

cd mozilla-central-*

copy toolkit\content\license.html "%SRC_DIR%"

cd testing\geckodriver

cargo install ^
    --no-track ^
    --locked ^
    --path . ^
    --profile release ^
    --root "%PREFIX%" ^
    || exit 1

cargo-bundle-licenses ^
    --format yaml ^
    --output "%SRC_DIR%\THIRDPARTY.yml" ^
    || exit 3

if not exist "%SCRIPTS%" md "%SCRIPTS%
move "%PREFIX%\bin\geckodriver.exe" "%SCRIPTS%"
