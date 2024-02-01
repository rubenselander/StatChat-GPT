from flask import Flask, request, jsonify, Response, render_template
from scripts.api_search import search_eurostat
from scripts.api_search import get_variables, get_data
import json

app = Flask(__name__)


@app.route("/privacy")
def index():
    return render_template("privacy.html")


@app.route("/searchForTables", methods=["GET"])
def search_tables():
    search_query = request.args.get("search_query")
    if not search_query:
        return jsonify({"error": "search_query is required"}), 400
    results = search_eurostat(search_query)
    return jsonify(results)


@app.route("/getVariables/<code>", methods=["GET"])
def variables(code):
    variables = get_variables(code)
    if not variables:
        return jsonify({"error": "No variables found for the provided code"}), 404
    return jsonify(variables)


@app.route("/getData/<code>", methods=["POST"])
def data(code):
    query = request.json
    if not query:
        return jsonify({"error": "Query is required"}), 400
    data = get_data(code, query)
    return Response(data, mimetype="text/csv")


if __name__ == "__main__":
    app.run(debug=True)

# # post parameters:
# # user_question: string. Required.
# # Description: searches for tables in Eurostat that match the user's question.
# @app.route("/search_for_tables", methods=["POST"])
# def search():
#     data = request.get_json()
#     print(json.dumps(data, indent=4, ensure_ascii=False))
#     search_string = data["query"]
#     # get the optional "year" parameter if it exists
#     # year = request.form.get("year", None)

#     search_results = search_eurostat(search_string)
#     return jsonify(search_results)


# # post parameters:
# # table_code: string. Required.
# # Description: gets the query schema for a table in Eurostat. The query schema is a JSON object that describes the variables and values that can be used to query the table.
# # Returns: a JSON object containing the query schema.
# # Notes: the query schema is used to format the parameters for the get_data endpoint.
# # The table_code parameter is the same as the "code" field in the search results.
# @app.route("/get_table_variables", methods=["POST"])
# def get_schema():
#     data = request.get_json()
#     code = data["table_code"]
#     variables = get_variables(code)
#     return jsonify(variables)


# # post parameters:
# # table_code: string. Required.
# # query: JSON object. Required.
# # Description: gets the data for a table in Eurostat. The query parameter is a JSON object that contains the parameters for the query.
# # Returns: a JSON object containing the data for the table.
# # Notes: the table_code parameter is the same as the "code" field in the search results.
# # The query parameter is a JSON object that contains the parameters for the query.
# @app.route("/get_table_data", methods=["POST"])
# def get_table_data():
#     data = request.get_json()
#     dataset_code = data["table_code"]
#     query = data["query"]
#     return jsonify(get_data(dataset_code, query))


# if __name__ == "__main__":
#     app.run(debug=True)


# def search_for_tables(search_query: str) -> list[dict]:
#     """Searches for tables in Eurostat that match the user's question.
#     The first time calling this function always use the users question as the search query.

#     Parameters:
#     search_query: string. Required.

#     Returns:
#     A list of dicts containing the search results. Each dict contains the following fields:
#     - code: string. The code of the table.
#     - text: string. The title of the table.
#     - date_start: int. The start year of the table.
#     - date_end: int. The end year of the table.
#     """
#     search_results = search_eurostat(search_query)
#     return search_results


# def get_variables(code: str) -> dict:
#     """Gets the variables for a given table.

#     Parameters:
#     code: string. Required. The code of the table as provided by the search_for_tables function.

#     Returns:
#     A dict containing the variables for the table in the following format:
#     {
#         "var_code_1": {
#             "text": "Variable description",
#             "values": {
#                 "value_code_1": "Value description",
#                 "value_code_2": "Value description",
#             }
#         },
#         "var_code_2": {
#             "text": "Variable description",
#             "values": {
#                 "value_code_1": "Value description",
#                 "value_code_2": "Value description",
#             }
#         },
#         ...
#     }
#     """
#     return local_get_variables(code)


# def get_data(code: str, query: dict) -> str:
#     """Gets the data for a given table and specified query.

#     Parameters:
#     code: string. Required. The code of the table as provided by the search_for_tables function.
#     query: dict. Required. Consists of variable and value codes from the get_variables function in the following format:
#     {
#         "time": ["2019"],
#         "geo": ["EU27_2020", "EU28"],
#         "unit": ["PC_ACT"]
#     }

#     Returns:
#     A csv string containing the data for the table in the following format:
#     "time","geo","unit","value"
#     "2019","EU27_2020","PC_ACT","6.2"
#     "2019","EU28","PC_ACT","6.3"
#     ...
#     """
#     return local_get_data(code, query)
