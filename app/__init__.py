import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api")
def api():
    return (
        jsonify(
            {
                "message": "Hello from Flask API on AWS Fargate, My name is Loi, I will become a senior developer!"
            }
        ),
        200,
    )


if __name__ == "__main__":
    # Use environment variables for configuration
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host = os.getenv("FLASK_HOST", "127.0.0.1")  # Default to localhost
    port = int(os.getenv("FLASK_PORT", "5000"))

    app.run(host=host, port=port, debug=debug_mode)
