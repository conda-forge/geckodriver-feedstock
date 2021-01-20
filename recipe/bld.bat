:: NOTE: mostly derived from
:: https://github.com/conda-forge/py-spy-feedstock/blob/master/recipe/bld.bat

cd testing/geckodriver

:: build
cargo install --locked --root "%PREFIX%" --path . || goto :error

:: remove extra build file
del /F /Q "%PREFIX%\.crates2.json"

goto :EOF

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%
