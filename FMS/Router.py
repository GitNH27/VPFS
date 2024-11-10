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
