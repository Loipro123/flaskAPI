from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api")
def api():
    return jsonify({"message": "Hello from Flask API on AWS Fargate!"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
