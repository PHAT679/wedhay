$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) {
    $edge = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}
& $edge --headless --disable-gpu --screenshot="static/images/screenshot_login.png" --window-size=1366,768 http://127.0.0.1:8000/accounts/login/
Write-Host "Screenshot done"
