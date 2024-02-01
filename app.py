from flask import Flask, render_template, request, jsonify
from scripts.api_search import search_eurostat, get_variables
from scripts.data_retriever import get_data

app = Flask(__name__)


@app.route("/privacy")
def index():
    return render_template("privacy.html")


# post parameters:
# user_question: string. Required.
# Description: searches for tables in Eurostat that match the user's question.
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
@app.route("/get_table_variables", methods=["POST"])
def get_schema():
    code = request.form["table_code"]
    variables = get_variables(code)
    return jsonify(variables)


# post parameters:
# table_code: string. Required.
# query: JSON object. Required.
# Description: gets the data for a table in Eurostat. The query parameter is a JSON object that contains the parameters for the query.
# Returns: a JSON object containing the data for the table.
# Notes: the table_code parameter is the same as the "code" field in the search results.
# The query parameter is a JSON object that contains the parameters for the query.
@app.route("/get_table_data", methods=["POST"])
def get_table_data():
    dataset_code = request.form["table_code"]
    query = request.form["query"]
    return jsonify(get_data(dataset_code, query))


if __name__ == "__main__":
    app.run(debug=True)
