@ECHO ON
rustc -V
cargo -V
cargo build --release --verbose
IF ERRORLEVEL 1 EXIT /B 1
cargo install --bin %PKG_NAME% --root %PREFIX%
IF ERRORLEVEL 1 EXIT /B 1
MOVE %PREFIX%\bin\%PKG_NAME%.exe %SCRIPTS%\%PKG_NAME%.exe
IF ERRORLEVEL 1 EXIT /B 1
DEL /F /Q %PREFIX%\.crates.toml
