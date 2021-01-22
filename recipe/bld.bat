:: NOTE: mostly derived from
:: https://github.com/conda-forge/py-spy-feedstock/blob/master/recipe/bld.bat

cd testing\geckodriver

:: build
cargo install --locked --root "%PREFIX%" --path . || goto :error

:: move to scripts
md %SCRIPTS% || echo "%SCRIPTS% already exists"
move %PREFIX%\bin\geckodriver.exe %SCRIPTS%

:: install cargo-license and dump licenses
set CARGO_LICENSES_FILE=%SRC_DIR%\%PKG_NAME%-%PKG_VERSION%-cargo-dependencies.json
cargo install cargo-license
set CARGO_LICENSE_BIN=%BUILD_PREFIX%\.cargo\bin\cargo-license
%CARGO_LICENSE_BIN% --json > %CARGO_LICENSES_FILE%
dir %CARGO_LICENSES_FILE%

:: remove extra build files
del /F /Q "%PREFIX%\.crates2.json"
del /F /Q "%PREFIX%\.crates.toml"

goto :EOF

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%
