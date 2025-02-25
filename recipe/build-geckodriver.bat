@echo on
set CARGO_PROFILE_RELEASE_STRIP=symbols

unzip license.zip
unzip testing.zip

robocopy "%SRC_DIR%\mozilla-central-*" "%SRC_DIR%" *.* /e /move

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
