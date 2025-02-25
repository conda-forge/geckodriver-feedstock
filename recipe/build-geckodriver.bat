:: NOTE: mostly derived from
:: https://github.com/conda-forge/py-spy-feedstock/blob/master/recipe/bld.bat

cd testing\geckodriver

:: build
cargo install --locked --root "%PREFIX%" --path . || goto :error

:: move to scripts
md %SCRIPTS% || echo "%SCRIPTS% already exists"
move %PREFIX%\bin\geckodriver.exe %SCRIPTS%

cargo-bundle-licenses --format yaml --output %SRC_DIR%\THIRDPARTY.yml

:: remove extra build files
del /F /Q "%PREFIX%\.crates2.json"
del /F /Q "%PREFIX%\.crates.toml"

goto :EOF

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%
