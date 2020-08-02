@ECHO ON
rustc -V
cargo -V

:: Install cargo-license
set CARGO_HOME=%BUILD_PREFIX%\cargo
mkdir %CARGO_HOME%
icacls %CARGO_HOME% /grant Users:F

cd testing\geckodriver

cargo build --release --verbose                   || goto :error
cargo install --root "%PREFIX%" --path .          || goto :error

if not exist "%SCRIPTS%" md "%SCRIPTS%"           || goto :error
move "%PREFIX%\bin\geckodriver.exe" "%SCRIPTS%"   || goto :error
del /F /Q "%PREFIX%\.crates.toml"
goto :EOF

:error
echo Failed with error #%errorlevel%.
exit 1
