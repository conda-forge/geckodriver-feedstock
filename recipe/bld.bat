:: NOTE: mostly derived from
:: https://github.com/conda-forge/py-spy-feedstock/blob/master/recipe/bld.bat

:: dump licenses
cargo-bundle-licenses --format yaml --output THIRDPARTY.yml

:: build
cargo install --locked --root "%PREFIX%" --path . || goto :error

:: move to scripts
md %SCRIPTS% || echo "%SCRIPTS% already exists"
move %PREFIX%\bin\geckodriver.exe %SCRIPTS%


:: remove extra build files
del /F /Q "%PREFIX%\.crates2.json"
del /F /Q "%PREFIX%\.crates.toml"

goto :EOF

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%
