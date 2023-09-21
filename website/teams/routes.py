from flask import Blueprint, render_template, request, redirect
import pandas as pd

teams_blueprint = Blueprint("teams", __name__)


@teams_blueprint.route("/", methods=["GET"])
def index():
    team_ids = pd.read_csv("TEAM_IDS.csv")
    teams = sorted([
        {"name": row.TEAM_NAME, "abrv": row.TEAM_ABRV} for row in team_ids.itertuples()
    ], key=lambda x: x['name'])

    return render_template("teams.html", teams=teams)


@teams_blueprint.route("/submit_team", methods=["POST"])
def submit_team():
    selected_team_abrv = request.form.get("team")
    # Handle the selected team here
    return redirect(f"/{selected_team_abrv}")
