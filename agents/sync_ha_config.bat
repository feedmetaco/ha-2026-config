@echo off
REM HA Sync Script - Sync Samba share to local directory
echo.
echo =====================================================
echo    HA Configuration Sync Tool
echo =====================================================
echo.

set "SOURCE=\\homeassistant.local\config"
set "DEST=c:\Users\Sami\Documents\ha-config"

echo Source: %SOURCE%
echo Destination: %DEST%
echo.
echo Starting sync...
echo.

robocopy "%SOURCE%" "%DEST%" /MIR /R:3 /W:5 ^
    /XD ".storage" "deps" "tts" "__pycache__" ".git" "backups" ^
    /XF "*.db" "*.db-shm" "*.db-wal" "*.log" "*.log.*" "home-assistant.log.fault" ^
    /NP /NFL /NDL

if %ERRORLEVEL% LEQ 7 (
    echo.
    echo =====================================================
    echo    Sync Completed Successfully!
    echo =====================================================
    echo.
    echo Your local ha-config directory now mirrors the Samba share
    echo.
) else (
    echo.
    echo =====================================================
    echo    Sync Failed - Error Code: %ERRORLEVEL%
    echo =====================================================
    echo.
)

pause

