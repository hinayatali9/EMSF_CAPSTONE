from flask import Blueprint, jsonify, render_template, request, session, url_for
import pandas as pd

preferences_blueprint = Blueprint("preferences", __name__)


@preferences_blueprint.route("/<team_abrv>", methods=["GET"])
def render_preferences_page(team_abrv: str):
    df_players = pd.read_csv("PLAYER_IDS.csv")
    team_ids_df = pd.read_csv("TEAM_IDS.csv")
    team_num_pick_df = pd.read_csv("draft_info/num_picks.csv")
    num_picks = pd.merge(team_ids_df, team_num_pick_df, on="TEAM_ID").query(
        "TEAM_ABRV == @team_abrv"
    )["NUM_PICKS"]
    return render_template(
        "preferences.html",
        players=df_players["PLAYER_NAME"],
        num_picks=int(num_picks.iloc[0]) if not num_picks.empty else 0,
        team_abrv=team_abrv,
    )


@preferences_blueprint.route("/<team_abrv>/submit_preferences", methods=["POST"])
def submit_preferences(team_abrv: str):
    input_info = request.get_json()
    session['min_max_constraints'] = pd.DataFrame(input_info["min_max_constraints"]).to_json()
    session['new_order'] = input_info["new_order"]
    session['positional_weight'] = 1 - int(input_info["positional_weight"])/10
    session['player_ids_picked'] = []
    session['current_pick'] = 1

    team_ids_df = pd.read_csv("TEAM_IDS.csv")
    draft_picks_df = pd.read_csv("draft_info/draft_pick_numbers.csv")
    draft_picks_df = pd.merge(
        team_ids_df, draft_picks_df, on=["TEAM_ID", "TEAM_NAME"]
    ).sort_values(by=["OVERALL_PICK"])

    session['available_team_picks'] = draft_picks_df.query('TEAM_ABRV == @team_abrv')['OVERALL_PICK'].to_list()

    return jsonify({'url': url_for('simulator.draft_simulator', team_abrv=team_abrv)})
