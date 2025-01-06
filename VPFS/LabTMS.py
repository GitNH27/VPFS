import FMS
from Team import Team
from flask import current_app as app, request

IDK = "IDK"

FMS.teams.clear()

@app.route("/Lab/AddTeam/<int:team>")
def serve_add_team(team: int):
    with FMS.mutex:
        if team in FMS.teams:
            return f"Already have team {team}"
        FMS.teams[team] = Team(team)
        return f"Added team {team}"

@app.route("/Lab/RemoveTeam/<int:team>")
def serve_remove_team(team: int):
    with FMS.mutex:
        if team in FMS.teams:
            FMS.teams.pop(team)
            return f"Removed team {team}"
        return f"No team {team} to remove"

@app.route("/Lab/ConfigMatch", methods=["post"])
def serve_config_match():
    num = request.json["number"]
    duration = request.json["duration"]
    FMS.cancel_match()
    FMS.config_match(num, duration)
    return ""

@app.route("/Lab/StartMatch", methods=["post"])
def serve_start_match():
    FMS.start_match()
    return ""
