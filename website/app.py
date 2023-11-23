import os
import binascii
from flask import Flask
from flask_session import Session
from preferences.routes import preferences_blueprint
from simulator.routes import simulator_blueprint
from teams.routes import teams_blueprint

app = Flask(__name__)
app.register_blueprint(teams_blueprint)
app.register_blueprint(preferences_blueprint)
app.register_blueprint(simulator_blueprint)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

secret_key = binascii.hexlify(os.urandom(24))
app.secret_key = secret_key


if __name__ == "__main__":
    app.run(debug=False)
