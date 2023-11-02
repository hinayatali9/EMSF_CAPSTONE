from typing import List
from flask import Blueprint, render_template, session
import pandas as pd
import numpy as np
import json
import draft_pick_prob.modelling.scripts.extract_probabilities as ep

simulator_blueprint = Blueprint("simulator", __name__)


@simulator_blueprint.route("/<team_abrv>/draft_simulator", methods=["GET"])
def draft_simulator(team_abrv):
    # Get data passed on from previous screen
    df_min_max_constraints = pd.DataFrame(json.loads(session["min_max_constraints"]))
    team_ranking_original = session["new_order"]
    positional_weight = int(session["positional_weight"])
    player_ids_picked: List[int] = session["player_ids_picked"]
    available_team_picks: List[int] = session["available_team_picks"]

    # Get static info
    df_player_positions = pd.read_csv("PLAYER_POSITIONS.csv")
    df_player_ids = pd.read_csv("PLAYER_IDS.csv")

    # Get pick probabilities
    pick_probs = ep.probability_available_pick_specified(
        players_ids_removed=player_ids_picked,
        num_simulations=100,
        pick_number=available_team_picks[0],
    )
    pick_probs = pd.merge(pick_probs, df_player_ids, on=["PLAYER_ID"])

    players_team_ranking = [
        {
            "position": df_player_positions.query("PLAYER_NAME == @player_name")[
                "Specific POS"
            ].iloc[0],
            "id": df_player_ids.query("PLAYER_NAME == @player_name")["PLAYER_ID"].iloc[
                0
            ],
            "name": player_name,
            "pick_prob": pick_probs.query("PLAYER_NAME == @player_name")[
                f"PICK_{available_team_picks[0]}"
            ].iloc[0],
        }
        for player_name in team_ranking_original
    ]

    team_ids_df = pd.read_csv("TEAM_IDS.csv")
    draft_picks_df = pd.read_csv("draft_info/draft_pick_numbers.csv")
    draft_picks_df = pd.merge(
        team_ids_df, draft_picks_df, on=["TEAM_ID", "TEAM_NAME"]
    ).sort_values(by=["OVERALL_PICK"])
    drafted_players_display = player_ids_picked.copy()
    drafted_players_display.extend(
        [""] * (len(draft_picks_df) - len(player_ids_picked))
    )
    draft_picks_df["PLAYER_NAME"] = drafted_players_display
    draft_picks = [
        {
            "team_abrv": row["TEAM_ABRV"],
            "team_name": row["TEAM_NAME"],
            "player_name": row["PLAYER_NAME"],
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
