from flask import Blueprint, render_template, request
import pandas as pd

preferences = Blueprint('preferences', __name__)

@preferences.route('/')
def render_preferences_page():
    df_players = pd.read_csv("PLAYER_IDS.csv")
    return render_template('preferences.html', players=df_players["PLAYER_NAME"])

@preferences.route('/submit_inputs', methods=['POST'])
def submit_inputs():
    input_info = request.get_json()
    df_min_max_constraints = pd.DataFrame(input_info["min_max_constraints"])
    new_order = input_info["new_order"]
    positional_weight = input_info["positional_weight"]
    print(df_min_max_constraints, new_order, positional_weight)  # Do something with the new order
    return '', 204
