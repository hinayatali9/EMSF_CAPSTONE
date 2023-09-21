from flask import Flask
from preferences.routes import preferences

app = Flask(__name__)
app.register_blueprint(preferences)


if __name__ == '__main__':
    app.run(debug=True)