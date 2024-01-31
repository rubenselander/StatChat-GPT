from flask import Flask, render_template, request, jsonify
from scripts.api_search import search_eurostat

app = Flask(__name__)


@app.route("/privacy")
def index():
    return render_template("privacy.html")


def get_query_schema(dataset_code: str) -> dict:
    """Gets the query schema for a given dataset."""
    return {}


def get_data(dataset_code: str, query: dict, response_format: str = "json") -> dict:
    """Gets the data from a table based on the given query."""
    return {}


# post parameters:
# user_question: string. Required.
# year: int. Optional.
# Description: searches for tables in Eurostat that match the user's question. If specified, the year parameter will filter the results to only include tables that contain data for that year.
# Returns: a JSON object containing the search results in the following format:
# {
#     "results": [
#         {
#             "code": "table_code1",
#             "title": "table_title1",
#             "source": "table_source1",
#             "date_start": <int>, # start year of the table data
#             "date_end": <int>, # end year of the table data
#             "variables": {
#                 "variable1_id": {"text": "variable1_text", "values": {"value1_id": "value1_text", "value2_id": "value2_text", ...}},
#                "variable2_id": {"text": "variable2_text", "values": {"value1_id": "value1_text", "value2_id": "value2_text", ...}},
#                ...
#          },
#          {
#             "code": "table_code2"...
#          }
#     ]
# }
@app.route("/search_for_tables", methods=["POST"])
def search():
    search_string = request.form["user_question"]
    # get the optional "year" parameter if it exists
    year = request.form.get("year", None)

    search_results = search_eurostat(search_string, year=year)
    return jsonify(search_results)


# post parameters:
# table_code: string. Required.
# Description: gets the query schema for a table in Eurostat. The query schema is a JSON object that describes the variables and values that can be used to query the table.
# Returns: a JSON object containing the query schema.
# Notes: the query schema is used to format the parameters for the get_data endpoint.
# The table_code parameter is the same as the "code" field in the search results.
@app.route("/get_query_instructions", methods=["POST"])
def get_schema():
    code = request.form["table_code"]
    return jsonify(get_query_schema(code))


# post parameters:
# table_code: string. Required.
# query: JSON object. Required.
# Description: gets the data for a table in Eurostat. The query parameter is a JSON object that contains the parameters for the query. The query schema is used to format the query parameters.
# Returns: a JSON object containing the data for the table.
# Notes: the table_code parameter is the same as the "code" field in the search results.
# The query parameter is a JSON object that contains the parameters for the query. The query schema should be constructed using the results from get_query_instructions endpoint.
@app.route("/get_data", methods=["POST"])
def get_data():
    dataset_code = request.form["table_code"]
    query = request.form["query"]
    return jsonify(get_data(dataset_code, query))


if __name__ == "__main__":
    app.run(debug=True)


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
