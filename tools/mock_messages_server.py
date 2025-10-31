"""Simple mock HTTP server that accepts POST /messages and returns JSON confirmation.

Run this locally to receive POSTs made by the `/relay` endpoint.
"""
from flask import Flask, request, jsonify

app = Flask("mock_messages_server")


@app.route("/messages", methods=["POST"])
def receive_messages():
    payload = request.get_json(silent=True)
    app.logger.info("Received POST /messages: %s", payload)
    return jsonify({"received": True, "payload": payload}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000)
