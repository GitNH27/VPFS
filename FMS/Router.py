from flask import Flask

app = Flask(__name__)

@app.route("/")
def serve_root():
    return "FMS is alive"