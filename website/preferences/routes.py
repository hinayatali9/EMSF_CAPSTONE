from flask import Blueprint, render_template, request
import pandas as pd

preferences_blueprint = Blueprint("preferences", __name__)


@preferences_blueprint.route("/<team_abrv>", methods=["GET"])
def render_preferences_page(team_abrv):
    df_players = pd.read_csv("PLAYER_IDS.csv")
    team_ids_df = pd.read_csv("TEAM_IDS.csv")
    team_num_pick_df = pd.read_csv("draft_info/num_picks.csv")
    num_picks = pd.merge(team_ids_df, team_num_pick_df, on="TEAM_ID").query(
        "TEAM_ABRV == @team_abrv"
    )["NUM_PICKS"]
    return render_template(
        "preferences.html",
        players=df_players["PLAYER_NAME"],
        num_picks=int(num_picks.iloc[0]),
        team_abrv=team_abrv,
    )


@preferences_blueprint.route("/preferences/submit_inputs", methods=["POST"])
def submit_preferences():
    input_info = request.get_json()
    df_min_max_constraints = pd.DataFrame(input_info["min_max_constraints"])
    new_order = input_info["new_order"]
    positional_weight = input_info["positional_weight"]
    print(
        df_min_max_constraints, new_order, positional_weight
    )  # Do something with the new order
    return "", 204
