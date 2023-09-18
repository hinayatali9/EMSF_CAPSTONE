from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    df_players = pd.read_csv("PLAYER_IDS.csv")
    return render_template('home.html', players=df_players["PLAYER_NAME"])

@app.route('/submit_inputs', methods=['POST'])
def submit_inputs():
    input_info = request.get_json()
    df_min_max_constraints = pd.DataFrame(input_info["min_max_constraints"])
    new_order = input_info["new_order"]
    positional_weight = input_info["positional_weight"]
    print(df_min_max_constraints, new_order, positional_weight)  # Do something with the new order
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)