#!/usr/bin/env python3
"""Flask API exposing /generate_ticket"""
from flask import Flask, request, jsonify
import json, pathlib, sys
sys.path.append(str(pathlib.Path(__file__).parent))
from pipeline import generate_ticket

app = Flask(__name__)

@app.route("/generate_ticket", methods=["POST"])
def gen():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    try:
        ticket = generate_ticket(data)
        return jsonify(ticket), 200
    except Exception as e:  # pragma: no cover
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
