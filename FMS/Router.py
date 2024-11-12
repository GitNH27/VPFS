from flask import Flask, jsonify
import FMS

app = Flask(__name__)

@app.route("/")
def serve_root():
    return "FMS is alive"

@app.route("/fares")
def serve_fares():
    data = []
    # Create copied list of data with desired information
    for idx, fare in enumerate(FMS.fares):
        data.append({
            "id": idx,
            "src": {
                "x": fare.src.x,
                "y": fare.src.y
            },
            "dest": {
                "x": fare.dest.x,
                "y": fare.dest.y
            },
            "claimed": fare.team is not None
        })
    return jsonify(data)

@app.route("/fares/claim/<int:idx>/<int:team>")
def claim_fare(idx: int, team: int):
    success = False
    message = ""
    if team in FMS.teams.keys():
        if idx < len(FMS.fares):
            if FMS.fares[idx].claim_fare(team):
                FMS.teams[team].currentFare = idx
                success = True
            else:
                message = "Fare already claimed"
        else:
            message = f"Could not find fare with ID {id}"
    else:
        message = f"Team {team} not in this match"

    return jsonify({
        "success": success,
        "message": message
    })

@app.route("/fares/current/<int:team>")
def current_fare(team: int):
    fare_dict = None
    message = ""
    if team in FMS.teams.keys():
        fare_idx = FMS.teams[team].currentFare
        if fare_idx is None:
            message = f"Team {team} does not have an active fare"
        else:
            fare = FMS.fares[fare_idx]
            fare_dict = {
                "id": fare_idx,
                "src": {
                    "x": fare.src.x,
                    "y": fare.src.y
                },
                "dest": {
                    "x": fare.dest.x,
                    "y": fare.dest.y
                },
                "claimed": fare.team is not None
            }
    else:
        message = f"Team {team} not in this match"

    return jsonify({
        "fare": fare_dict,
        "message": message
    })

@app.route("/whereami/<int:team>")
def whereami_get(team: int):
    point = None
    last_update : int = 0
    message = ""
    if team in FMS.teams.keys():
        team = FMS.teams[team]
        point = {
            "x": team.pos.x,
            "y": team.pos.y
        },
        last_update = team.lastPosUpdate
    else:
        message = f"Team {team} not in this match"

    return jsonify({
        "position": point,
        "last_update": last_update,
        "message": message
    })
