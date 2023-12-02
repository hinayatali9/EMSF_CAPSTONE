export FLASK_APP=website/app.py
export FLASK_ENV=production
export PYTHONPATH=$(pwd)

flask run
