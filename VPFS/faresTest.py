import time
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from threading import Thread
from jsonschema.exceptions import ValidationError
from jsonschema import validate
from Utils import Point
import FMS
from Auth import authenticate

app = Flask(__name__)
sock = SocketIO(app)

operatingMode = "lab"
app.app_context().push()
if operatingMode == "lab":
    import LabTMS
    LabTMS.IDK = ""

# Define the PositionPrinter class
class PositionPrinter:
    def __init__(self, team_id):
        self.team_id = team_id
        self.start_pos = None
        self.end_pos = None

    def print_start_end_positions(self):
        # Check if Team exists in FMS.teams
        if self.team_id not in FMS.teams:
            print(f"Team {self.team_id} not found. Creating Team {self.team_id} with default position.")
            # If team is not found, create a default position (0, 0) for Team 1
            FMS.teams[self.team_id] = Point(0, 0)  # Create team with Point(0, 0) position
            
        team_pos = FMS.teams.get(self.team_id)
        if team_pos:
            # Start position
            self.start_pos = (team_pos.x, team_pos.y)
            print(f"Start position for Team {self.team_id}: {self.start_pos}")
            
            # Simulating position change after 5 seconds
            time.sleep(5)  # Simulating a delay for position update
            
            # End position
            self.end_pos = (team_pos.x, team_pos.y)
            print(f"End position for Team {self.team_id}: {self.end_pos}")
        else:
            print(f"Team {self.team_id} not found in FMS.teams.")

@app.route("/")
def serve_root():
    return "VPFS is alive\n"

@app.route("/whereami/<int:team>")
def whereami_get(team: int):
    point = None
    last_update: int = 0
    message = ""
    if team in FMS.teams.keys():
        team_pos = FMS.teams[team]
        point = {
            "x": team_pos.x,
            "y": team_pos.y
        }
        last_update = time.time()
    else:
        message = f"Team {team} not in this match"

    return jsonify({
        "position": point,
        "last_update": last_update,
        "message": message
    })

# Socket endpoints
@sock.on("connect")
def sock_connect(auth):
    print("Connected")

@sock.on("disconnect")
def sock_disconnect():
    print("Disconnected")

whereami_update_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "team": {"type": "number"},
            "x": {"type": "number"},
            "y": {"type": "number"},
        },
        "required": ["team", "x", "y"],
    },
}

@sock.on("whereami_update")
def whereami_update(json):
    print(f"Recv whereami update from {request.remote_addr}")
    try:
        validate(json, schema=whereami_update_schema)
        for entry in json:
            team = entry['team']
            x = entry['x']
            y = entry['y']
            if team in FMS.teams.keys():
                FMS.teams[team] = Point(x, y)  # Updating the team position directly
            else:
                print(f"Team not in match {team}")
    except ValidationError as e:
        print(f"Validation failed: {e}")

if __name__ == "__main__":
    # Specify the team ID you want to print the position for (e.g., Team 1)
    team_id = 1
    position_printer = PositionPrinter(team_id)
    
    # Start printing positions (start and end)
    position_printer.print_start_end_positions()
    
    # Running Flask app
    Thread(target=FMS.periodic, daemon=True).start()
    sock.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True)
