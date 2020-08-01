@ECHO ON
rustc -V
cargo -V

cd testing\geckodriver

:: Install cargo-license
set CARGO_HOME=%BUILD_PREFIX%\cargo
mkdir %CARGO_HOME%
icacls %CARGO_HOME% /grant Users:F

:: Don't check these on windows because slow, and weird build dep errors
::
:: cargo install cargo-license || goto :error
::
:: :: Check that all downstream libraries licenses are present
:: set PATH=%PATH%;%CARGO_HOME%\bin
:: cargo-license --json > dependencies.json || goto :error
:: type dependencies.json || goto :error
:: python %RECIPE_DIR%\check_licenses.py || goto :error

cargo build --release --verbose                   || goto :error
cargo install --root "%PREFIX%" --path .          || goto :error

if not exist "%SCRIPTS%" md "%SCRIPTS%"           || goto :error
move "%PREFIX%\bin\geckodriver.exe" "%SCRIPTS%"   || goto :error
del /F /Q "%PREFIX%\.crates.toml"
goto :EOF

:error
echo Failed with error #%errorlevel%.
exit 1
