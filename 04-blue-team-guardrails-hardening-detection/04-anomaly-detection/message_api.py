
from flask import Flask, request, jsonify

from anomaly_detector import monitor_api_request

app = Flask(__name__)


@app.route("/message", methods=["POST"])
def receive_message():

    data = request.get_json(silent=True) or {}

    identity = data.get("identity", "agent_A")
    message = data.get("message", "")

    # Monitor every incoming API request
    monitor_api_request(identity)

    # Harmless operation
    print("Message received:", message)

    return jsonify({
        "status": "success",
        "message": "Message received successfully"
    }), 200


if __name__ == "__main__":

    print("Starting local Message API...")
    print("Endpoint: http://127.0.0.1:5000/message")
    print("Threshold: 20 requests in 60 seconds")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
