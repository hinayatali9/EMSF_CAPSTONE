from flask import Flask
from preferences.routes import preferences_blueprint
from teams.routes import teams_blueprint

app = Flask(__name__)
app.register_blueprint(preferences_blueprint)
app.register_blueprint(teams_blueprint)


if __name__ == "__main__":
    app.run(debug=True)
