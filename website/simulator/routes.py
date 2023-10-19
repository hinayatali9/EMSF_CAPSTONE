from flask import Blueprint, render_template
import pandas as pd

simulator_blueprint = Blueprint("simulator", __name__)


@simulator_blueprint.route("/draft_simulator/<team_abrv>", methods=["GET"])
def draft_simulator(team_abrv):
    # Fetch your data here
    df_player_positions = pd.read_csv("PLAYER_POSITIONS.csv")
    players_team_ranking = [
        {
            "position": row["Specific POS"],
            "id": row["PLAYER_ID"],
            "name": row["PLAYER_NAME"],
            "pick_prob": 1,
        }
        for _, row in df_player_positions.iterrows()
    ]

    team_ids_df = pd.read_csv("TEAM_IDS.csv")
    draft_picks_df = pd.read_csv("draft_info/draft_pick_numbers.csv")
    draft_picks_df = pd.merge(
        team_ids_df, draft_picks_df, on=["TEAM_ID", "TEAM_NAME"]
    ).sort_values(by=["OVERALL_PICK"])
    draft_picks = [
        {
            "team_abrv": row["TEAM_ABRV"],
            "team_name": row["TEAM_NAME"],
            "player_name": "",
        }
        for _, row in draft_picks_df.iterrows()
    ]

    suggested_player = [
        {"id": 1, "position": "C", "name": "Connor Bedard", "pick_prob": 1}
    ]  # only one entry, use list to ignore html if empty
    next_pick_number = 19

    players_pick_prob_ranking = sorted(
        players_team_ranking, key=lambda x: x["pick_prob"]
    )
    return render_template(
        "simulator.html",
        team_abrv=team_abrv,
        players_team_ranking=players_team_ranking,
        draft_picks=draft_picks,
        suggested_player=suggested_player,
        next_pick_number=next_pick_number,
        players_pick_prob_ranking=players_pick_prob_ranking,
    )
