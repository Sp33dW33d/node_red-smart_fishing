@echo off
setlocal
cd /d "%~dp0"

echo Keeping the WSL Docker engine alive while this launcher is open...
set "WSL_KEEPALIVE_PID="
for /f "usebackq delims=" %%P in (`powershell.exe -NoProfile -Command "$p = Start-Process -FilePath 'wsl.exe' -ArgumentList '--exec sleep infinity' -WindowStyle Hidden -PassThru; $p.Id"`) do set "WSL_KEEPALIVE_PID=%%P"
if not defined WSL_KEEPALIVE_PID goto :wsl_keepalive_failed

echo Starting Smart Fishing services through WSL Docker Compose...
wsl.exe -e sh -lc "docker compose up -d"
if errorlevel 1 goto :startup_failed

set "NODE_RED_PORT="
for /f "tokens=2 delims=:" %%P in ('wsl.exe -e sh -lc "docker compose port node-red 1880"') do set "NODE_RED_PORT=%%P"
if not defined NODE_RED_PORT goto :port_failed

set "BASE_URL=http://localhost:%NODE_RED_PORT%"
echo Waiting for Node-RED at %BASE_URL% ...
powershell.exe -NoProfile -Command "$url='%BASE_URL%/dashboard/overview'; $deadline=(Get-Date).AddSeconds(120); do { try { $response=Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 3; if ($response.StatusCode -eq 200) { exit 0 } } catch { }; Start-Sleep -Seconds 2 } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 goto :not_ready

echo Opening the Node-RED flow editor and dashboard...
start "" "%BASE_URL%/#flow/a100000000000001"
start "" "%BASE_URL%/dashboard/overview"
set "EXIT_CODE=0"
goto :wait_to_quit

:startup_failed
echo.
echo Docker Compose could not start. Check that the WSL Docker engine is running.
set "EXIT_CODE=1"
goto :wait_to_quit

:port_failed
echo.
echo Could not determine the Node-RED host port from Docker Compose.
set "EXIT_CODE=1"
goto :wait_to_quit

:not_ready
echo.
echo Node-RED did not respond within 120 seconds. Recent logs:
wsl.exe -e sh -lc "docker compose logs --tail=50 node-red history-cache"
set "EXIT_CODE=1"
goto :wait_to_quit

:wait_to_quit
echo.
echo Press q to stop the project and close this launcher.
choice /c q /n >nul
if defined WSL_KEEPALIVE_PID (
    echo Stopping the Smart Fishing containers...
    wsl.exe -e sh -lc "docker compose down"
    echo Waiting for the WSL keepalive to exit...
)
call :release_wsl_keepalive
exit /b %EXIT_CODE%

:wsl_keepalive_failed
echo.
echo Could not keep the WSL Docker engine running. Check that WSL is available.
set "EXIT_CODE=1"
goto :wait_to_quit

:release_wsl_keepalive
if not defined WSL_KEEPALIVE_PID exit /b 0
powershell.exe -NoProfile -Command "Stop-Process -Id %WSL_KEEPALIVE_PID% -Force -ErrorAction SilentlyContinue; Wait-Process -Id %WSL_KEEPALIVE_PID% -ErrorAction SilentlyContinue"
exit /b 0
