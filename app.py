from flask import Flask, render_template, request, jsonify
from scripts.data_functions import (
    get_json_test_data,
    get_csv_test_data,
    set_url_to_csv_map,
    set_url_to_responses_map,
)

app = Flask(__name__)

# set_url_to_csv_map()

set_url_to_responses_map()


@app.route("/privacy")
def index():
    return render_template("privacy.html")


@app.route("/get_json_test_data", methods=["GET"])
def handle_get_json_test_data():
    test_url = request.args.get("test_url")
    return jsonify(get_json_test_data(test_url))


@app.route("/get_csv_test_data", methods=["GET"])
def handle_get_csv_test_data():
    test_url = request.args.get("test_url")
    return get_csv_test_data(test_url), 200, {"Content-Type": "text/csv"}


if __name__ == "__main__":
    app.run(debug=True)

# @app.route("/get_small_json_test_data", methods=["GET"])
# def handle_get_small_json_test_data():
#     test_url = request.args.get("test_url")
#     return jsonify(get_small_json_test_data(test_url))


# @app.route("/get_text_test_data", methods=["GET"])
# def handle_get_text_test_data():
#     test_url = request.args.get("test_url")
#     return get_text_test_data(test_url)


# @app.route("/get_numerical_test_data", methods=["GET"])
# def handle_get_numerical_test_data():
#     test_url = request.args.get("test_url")
#     return jsonify(get_numerical_test_data(test_url))


# @app.route("/ask", methods=["POST"])
# def ask():
#     """Handles incoming user questions and returns a JSON response."""
#     question = request.form["question"]

#     print(question)

#     try:
#         answer_dict = get_answer(question)
#         answer = answer_dict["answer"]
#         title = answer_dict["title"]
#         url = answer_dict["url"]
#         source = answer_dict["source"]

#         # Use HTML tags for formatting
#         response = f"{answer} <br><br><b>Källa:</b> {source} <br><b>Tabell:</b> {title} <br><b>Länk till tabellen:</b> <a href='{url}'>{url}</a>"
#         return jsonify({"response": response})
#     except Exception as e:
#         print(e)
#         return jsonify({"response": "Något gick fel. Försök igen."})
