@echo off
setlocal
cd /d "%~dp0"

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
exit /b 0

:startup_failed
echo.
echo Docker Compose could not start. Check that the WSL Docker engine is running.
pause
exit /b 1

:port_failed
echo.
echo Could not determine the Node-RED host port from Docker Compose.
pause
exit /b 1

:not_ready
echo.
echo Node-RED did not respond within 120 seconds. Recent logs:
wsl.exe -e sh -lc "docker compose logs --tail=50 node-red history-cache"
pause
exit /b 1
