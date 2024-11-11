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
    if idx < len(FMS.fares):
        success = FMS.fares[idx].claim_fare(team)
        if not success:
            message = "Fare already claimed"
    else:
        message = "Could not find fare ID"

    return jsonify({
        "success": success,
        "message": message
    })