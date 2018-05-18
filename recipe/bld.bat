@ECHO ON
rustc -V
cargo -V
cargo build --release --verbose
IF ERRORLEVEL 1 EXIT /B 1
cargo install --bin %PKG_NAME% --root %PREFIX%
IF ERRORLEVEL 1 EXIT /B 1
MKDIR %LIBRARY_BIN%
MOVE %PREFIX%\%PKG_NAME%.exe %LIBRARY_BIN%\
IF ERRORLEVEL 1 EXIT /B 1
DEL /F /Q %PREFIX%\.crates.toml
