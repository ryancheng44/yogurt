from flask import Flask, request, jsonify, render_template

import atexit
import yogurt  # this would be your existing agent logic

app = Flask(__name__)


@app.route("/")
def index():
    if not yogurt.setup_vector_store():
        return render_template("error.html")
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = (request.get_json(silent=True) or {}).get("message", "")
    response = yogurt.handle_query(user_input)
    return jsonify({"response": response})


@app.route("/cleanup", methods=["POST"])
def cleanup():
    yogurt.cleanup()
    return "", 204


atexit.register(cleanup)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
