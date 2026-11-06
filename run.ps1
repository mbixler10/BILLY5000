# Run BILLY5000 in the browser emulator (http://localhost:8888).
# Frees port 8888 first so a leftover run never blocks you.
# Pass extra options straight through, e.g.  .\run.ps1 --at "2026-12-24 18:00"

Get-NetTCPConnection -LocalPort 8888 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Set-Location $PSScriptRoot
python main.py @args
