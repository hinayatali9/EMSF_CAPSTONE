from typing import List, Dict, Any
from flask import Blueprint, jsonify, render_template, request, session
import pandas as pd
import json
import draft_pick_prob.modelling.scripts.extract_probabilities as ep

simulator_blueprint = Blueprint("simulator", __name__)


@simulator_blueprint.route("/<team_abrv>/draft_simulator", methods=["GET"])
def draft_simulator(team_abrv):
    # Get data passed on from previous screen
    team_ranking_original = session["original_order"]
    team_ranking_new = session["new_order"]
    player_ids_picked: List[int] = session["player_ids_picked"]
    available_team_picks: List[int] = session["available_team_picks"]
    positional_weight = float(session["positional_weight"])

    # Get static info
    df_player_positions = pd.read_csv("PLAYER_POSITIONS.csv")
    df_player_ids = pd.read_csv("PLAYER_IDS.csv")

    is_next_pick_team_draft_pick = (len(session["player_ids_picked"]) + 1) in session[
        "available_team_picks"
    ]

    pick_index = is_next_pick_team_draft_pick

    # Get pick probabilities
    df_player_ids["PLAYER_NAME"] = pd.Categorical(
        df_player_ids["PLAYER_NAME"], categories=team_ranking_original, ordered=True
    )
    df_player_ids.sort_values("PLAYER_NAME", inplace=True)

    df_player_values = ep.player_value(
        player_rankings=df_player_ids,
        player_position=df_player_positions,
        picks_taken=player_ids_picked,
        user_weight=positional_weight,
        team_name=team_abrv,
    )

    pick_probs = ep.probability_available_pick_specified(
        players_ids_removed=player_ids_picked,
        num_simulations=100,
        pick_number=available_team_picks[pick_index],
    )
    pick_probs = pd.merge(pick_probs, df_player_ids, on=["PLAYER_ID"])
    df_player_values = pd.merge(df_player_ids, df_player_values, on=["PLAYER_ID"])

    players_team_ranking = [
        {
            "position": df_player_positions.query("PLAYER_NAME == @player_name")[
                "POS"
            ].iloc[0],
            "id": df_player_ids.query("PLAYER_NAME == @player_name")["PLAYER_ID"].iloc[
                0
            ],
            "name": player_name,
            "pick_prob": float(
                pick_probs.query("PLAYER_NAME == @player_name")[
                    f"PICK_{available_team_picks[pick_index]}"
                ]
                .iloc[0]
                .round(4)
            ),
            "player_value": float(
                df_player_values.query("PLAYER_NAME == @player_name")["VALUE"]
                .iloc[0]
                .round(4)
            ),
        }
        for player_name in team_ranking_new
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

    suggested_player = (
        suggest_a_player(team_abrv, pick_probs) if is_next_pick_team_draft_pick else []
    )

    next_pick_number = (
        available_team_picks[1]
        if available_team_picks[0] == 1
        else available_team_picks[0]
    )

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
        is_next_pick_team_draft_pick=is_next_pick_team_draft_pick,
    )


@simulator_blueprint.route("/<team_abrv>/api/draft", methods=["POST"])
def api_draft(team_abrv):
    # Extract the player_id from the request body
    data = request.get_json()
    player_picked_id = int(data.get("player_id"))

    session["available_team_picks"].pop(0)

    (
        is_next_pick_team_draft_pick,
        players_team_ranking,
        draft_picks,
        next_pick_number,
        players_pick_prob_ranking,
        pick_probs,
    ) = move_one_pick_forward(player_picked_id, team_abrv)

    suggested_player = (
        suggest_a_player(team_abrv, pick_probs) if is_next_pick_team_draft_pick else []
    )

    return jsonify(
        {
            "is_next_pick_team_draft_pick": is_next_pick_team_draft_pick,
            "players_team_ranking": players_team_ranking,
            "draft_picks": draft_picks,
            "suggested_player": suggested_player,
            "next_pick_number": next_pick_number,
            "players_pick_prob_ranking": players_pick_prob_ranking,
        }
    )


@simulator_blueprint.route("/<team_abrv>/api/simulate_pick", methods=["POST"])
def api_simulate_pick(team_abrv):
    # For Your Next Pick, use while not is_next_pick_team_draft_pick, suggest player in the end
    # For Next Pick, run once, check is_next_pick_team_draft_pick; if so, suggest player in the end
    data = request.get_json()
    button_id = data.get("button_id")

    player_picked_id = int(ep.simulate_one_player_taken(session["player_ids_picked"]))
    (
        is_next_pick_team_draft_pick,
        players_team_ranking,
        draft_picks,
        next_pick_number,
        players_pick_prob_ranking,
        pick_probs,
    ) = move_one_pick_forward(player_picked_id, team_abrv)

    if button_id == "yourNextPick":
        while not is_next_pick_team_draft_pick:
            player_picked_id = int(
                ep.simulate_one_player_taken(session["player_ids_picked"])
            )
            (
                is_next_pick_team_draft_pick,
                players_team_ranking,
                draft_picks,
                next_pick_number,
                players_pick_prob_ranking,
                pick_probs,
            ) = move_one_pick_forward(player_picked_id, team_abrv)

    suggested_player = (
        suggest_a_player(team_abrv, pick_probs) if is_next_pick_team_draft_pick else []
    )

    return jsonify(
        {
            "is_next_pick_team_draft_pick": is_next_pick_team_draft_pick,
            "players_team_ranking": players_team_ranking,
            "draft_picks": draft_picks,
            "suggested_player": suggested_player,
            "next_pick_number": next_pick_number,
            "players_pick_prob_ranking": players_pick_prob_ranking,
        }
    )


def move_one_pick_forward(player_picked_id: int, team_abrv: str):
    # Get static info
    df_player_positions = pd.read_csv("PLAYER_POSITIONS.csv")
    df_player_ids = pd.read_csv("PLAYER_IDS.csv")

    player_picked_name = df_player_ids.query(f"PLAYER_ID == {player_picked_id}")[
        "PLAYER_NAME"
    ].iloc[0]

    # Update previous data given selected player
    session["new_order"].remove(player_picked_name)
    session["player_ids_picked"].append(int(player_picked_id))

    # Get data passed on from previous screen
    team_ranking_new = session["new_order"]
    team_ranking_original = session["original_order"]
    player_ids_picked: List[int] = session["player_ids_picked"]
    available_team_picks: List[int] = session["available_team_picks"]
    positional_weight = float(session["positional_weight"])

    is_next_pick_team_draft_pick = (len(session["player_ids_picked"]) + 1) in session[
        "available_team_picks"
    ]

    pick_index = is_next_pick_team_draft_pick

    # Get pick probabilities
    df_player_ids["PLAYER_NAME"] = pd.Categorical(
        df_player_ids["PLAYER_NAME"], categories=team_ranking_original, ordered=True
    )
    df_player_ids.sort_values("PLAYER_NAME", inplace=True)

    df_player_values = ep.player_value(
        player_rankings=df_player_ids,
        player_position=df_player_positions,
        picks_taken=player_ids_picked,
        user_weight=positional_weight,
        team_name=team_abrv,
    )
    pick_probs = ep.probability_available_pick_specified(
        players_ids_removed=player_ids_picked,
        num_simulations=100,
        pick_number=available_team_picks[pick_index],
    )
    pick_probs = pd.merge(pick_probs, df_player_ids, on=["PLAYER_ID"])
    df_player_values = pd.merge(df_player_ids, df_player_values, on=["PLAYER_ID"])

    players_team_ranking = [
        {
            "position": df_player_positions.query("PLAYER_NAME == @player_name")[
                "POS"
            ].iloc[0],
            "id": int(
                df_player_ids.query("PLAYER_NAME == @player_name")["PLAYER_ID"].iloc[0]
            ),
            "name": player_name,
            "pick_prob": float(
                pick_probs.query("PLAYER_NAME == @player_name")[
                    f"PICK_{available_team_picks[pick_index]}"
                ]
                .iloc[0]
                .round(4)
            ),
            "player_value": float(
                df_player_values.query("PLAYER_NAME == @player_name")["VALUE"]
                .iloc[0]
                .round(4)
            ),
        }
        for player_name in team_ranking_new
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
    draft_picks_df["PLAYER_ID"] = drafted_players_display
    draft_picks = [
        {
            "team_abrv": row["TEAM_ABRV"],
            "team_name": row["TEAM_NAME"],
            "player_name": df_player_ids.query("PLAYER_ID == @row['PLAYER_ID']")[
                "PLAYER_NAME"
            ].iloc[0]
            if not df_player_ids.query("PLAYER_ID == @row['PLAYER_ID']").empty
            else "",
        }
        for _, row in draft_picks_df.iterrows()
    ]

    players_pick_prob_ranking = sorted(
        players_team_ranking, key=lambda x: x["pick_prob"]
    )

    is_next_pick_team_draft_pick = (len(session["player_ids_picked"]) + 1) in session[
        "available_team_picks"
    ]

    next_pick_number = available_team_picks[is_next_pick_team_draft_pick]

    return (
        is_next_pick_team_draft_pick,
        players_team_ranking,
        draft_picks,
        next_pick_number,
        players_pick_prob_ranking,
        pick_probs,
    )


def suggest_a_player(team_abrv, pick_probs):
    df_player_positions = pd.read_csv("PLAYER_POSITIONS.csv")
    df_player_ids = pd.read_csv("PLAYER_IDS.csv")
    team_needs_df = pd.read_csv("./Prospect Pool/percentiles.csv", index_col=0)

    df_min_max_constraints = pd.Series(json.loads(session["min_max_constraints"]))
    team_ranking_original = session["original_order"]
    positional_weight = float(session["positional_weight"])
    player_ids_picked: List[int] = session["player_ids_picked"]
    available_team_picks: List[int] = session["available_team_picks"]

    df_player_ids["PLAYER_NAME"] = pd.Categorical(
        df_player_ids["PLAYER_NAME"], categories=team_ranking_original, ordered=True
    )
    df_player_ids.sort_values("PLAYER_NAME", inplace=True)

    df_player_values = ep.player_value(
        player_rankings=df_player_ids,
        player_position=df_player_positions,
        picks_taken=player_ids_picked,
        user_weight=positional_weight,
        team_name=team_abrv,
    )

    df_player_values = pd.merge(df_player_ids, df_player_values, on=["PLAYER_ID"])

    suggested_player_id = ep.determine_optimal_pick(
        player_rankings=df_player_ids,
        player_position=df_player_positions,
        team_needs=team_needs_df,
        team=team_abrv,
        pick_numbers_left=available_team_picks,
        picks_taken=player_ids_picked,
        max_pos_const=cast_dict_vals_to_int(df_min_max_constraints["max_picks"]),
        min_pos_const=cast_dict_vals_to_int(df_min_max_constraints["min_picks"]),
        user_weight=positional_weight,
    )

    suggested_player = [
        {
            "position": df_player_positions.query("PLAYER_ID == @suggested_player_id")[
                "POS"
            ].iloc[0],
            "id": int(suggested_player_id),
            "name": df_player_positions.query("PLAYER_ID == @suggested_player_id")[
                "PLAYER_NAME"
            ].iloc[0],
            "pick_prob": float(
                pick_probs.query("PLAYER_ID == @suggested_player_id")[
                    f"PICK_{available_team_picks[1]}"
                ]
                .iloc[0]
                .round(4)
            ),
            "player_value": float(
                df_player_values.query("PLAYER_ID == @suggested_player_id")["VALUE"]
                .iloc[0]
                .round(4)
            ),
        }
    ]  # only one entry, use list to ignore html if empty

    return suggested_player


def cast_dict_vals_to_int(my_dict: Dict[Any, str]):
    return {k: int(v) for k, v in my_dict.items()}
