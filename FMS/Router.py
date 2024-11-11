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
    fare_idx = FMS.teams[team].currentFare
    fare = FMS.fares[fare_idx]
    return jsonify({
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
    })