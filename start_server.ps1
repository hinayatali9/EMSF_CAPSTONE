$env:FLASK_APP="website/app.py"
$env:FLASK_ENV="production"
$env:PYTHONPATH = Get-Location

flask run
