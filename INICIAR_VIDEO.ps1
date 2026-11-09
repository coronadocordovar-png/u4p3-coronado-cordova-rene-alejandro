Set-Location $PSScriptRoot
if (-not (Test-Path '.\venv\Scripts\python.exe')) {
    py -m venv venv
}
& '.\venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\venv\Scripts\python.exe' manage.py check
& '.\venv\Scripts\python.exe' manage.py migrate
Write-Host 'LISTO: abre otra terminal para runserver o pulsa Enter para iniciarlo'
Read-Host
& '.\venv\Scripts\python.exe' manage.py runserver
