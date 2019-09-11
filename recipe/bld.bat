@ECHO ON
rustc -V
cargo -V
cargo build --release --verbose                   || goto :error
cargo install --root "%PREFIX%" --path .          || goto :error
if not exist "%SCRIPTS%" md "%SCRIPTS%"           || goto :error
move "%PREFIX%\bin\geckodriver.exe" "%SCRIPTS%"   || goto :error
del /F /Q "%PREFIX%\.crates.toml"
goto :EOF

:error
echo Failed with error #%errorlevel%.
exit 1
