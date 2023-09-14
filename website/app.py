from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    df_players = pd.read_csv("PLAYER_IDS.csv")
    return render_template('home.html', players=df_players["PLAYER_NAME"])

@app.route('/reorder', methods=['POST'])
def reorder():
    new_order = request.get_json()
    print(new_order)  # Do something with the new order
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)