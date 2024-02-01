

File: C:\Users\Admin\Documents\StatChat-GPT\app.py
```python
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

```



File: C:\Users\Admin\Documents\StatChat-GPT\Article.md
# StatChat: Building a Statistical Research GPT with DeepLake and Eurostat
In this article we will build a GPT that can answer statistical questions using DeepLake and the Eurostat API. We will also show you how to improve the performance of the GPT by using Deep Memory and reranking with Cohere.


## Introduction
Open data is great but it can be hard to find the data you need. Eurostat is the statistical office of the European Union and provides a lot of open, reliable data. However, finding the data you need can be a challenge. This is especially true if you don't have experience with finding and interacting with statistical databases. This is where our GPT comes in. It not only finds the data we need but also presents it in a way that is easy to understand and use. 

## Why not just use ChatGPT? 
Well, ChatGPT is great at answering questions but say you want to know something like "How has France's CO2 emissions changed since 1990?" or "Does life expectancy in the EU correlate with GDP per capita?", these are questions that require data to answer and are also not findable through a simple google search.

## Why not another vector store?
1. Deeplake is open source
2. Deeplake offers "Deep Memory" which will greatly improve the search performance and our GPTs ability to find relevant datasets.
<!-- - Define Deep Memory -->
<!-- Personal reasons: -->
3. Local development and usage is serverless making it so much easier and faster to both develop and use in your projects.  
4. Going from local, serverless, to a fully hosted solution literally takes 1 line of code. Maybe 2 if you want to be exact.
```python
from deeplake import deepcopy
deepcopy(src="<path to local deeplake>", dest="<path to new hosted instance>")
# That's it!
```
5. Simple and easy to use. Well documented and active community.
6. I've literally never interacted with a more accessible and helpful developer team than the one behind deeplake, ActiveLoop.







Deeplake is a open source vector store. We are going to use a local flask based api that allows the GPT to search for suiting and relevant datasets through natural language and filters. The local api acts as a bridge between the deeplake vector store and our GPT. Once the GPT has found a dataset/table it can use it can then perform an api call to eurostat api and retrieve the relevant data using the dataset code and variables (for which it specifies a selection that determines the data it needs). The code and corresponding variables is from our deeplake dataset.











File: C:\Users\Admin\Documents\StatChat-GPT\openapi.yaml
```yaml
openapi: 3.0.0
info:
  title: Eurostat Data API
  description: API for searching and retrieving data from Eurostat
  version: 1.0.0

servers:
  - url: https://statchat-nlzq.onrender.com

paths:
  /privacy:
    get:
      operationId: getPrivacyPolicy
      summary: Privacy Policy
      description: Returns the privacy policy page.
      responses:
        200:
          description: Privacy policy page
          content:
            text/html:
              schema:
                type: string

  /search_for_tables:
    post:
      operationId: searchForTables
      summary: Search Eurostat Tables
      description: Searches for tables in Eurostat that match the user's question.
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                user_question:
                  type: string
                  description: The question the user is asking.
              required:
                - user_question
      responses:
        200:
          description: Search results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResults'

  /get_table_variables:
    post:
      operationId: getTableVariables
      summary: Get Table Variables
      description: Gets the variables for a table in Eurostat.
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                table_code:
                  type: string
                  description: Code of the Eurostat table.
              required:
                - table_code
      responses:
        200:
          description: Variables for the table
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TableVariables'

  /get_table_data:
    post:
      operationId: getData
      summary: Get Data for Table
      description: >
        Retrieves table data based on query parameters as JSON. The query keys 
        correspond to variable IDs from `get_table_variables`. The response is 
        a CSV string with column headers as variables.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                table_code:
                  type: string
                  description: Code of the Eurostat table.
                query:
                  type: object
                  description: >
                    JSON object containing parameters for the query. 
                    The keys are variable IDs/codes corresponding to those provided 
                    by the `get_table_variables` endpoint. For non specified variables, 
                    all values are returned.
                  additionalProperties:
                    type: array
                    items:
                      type: string
              required:
                - table_code
      responses:
        200:
          description: CSV data for the specified table
          content:
            text/csv:
              schema:
                type: string
                description: CSV formatted string. The first row contains column headers (variables).

components:
  schemas:
    SearchResults:
      type: object
      properties:
        results:
          type: array
          items:
            $ref: '#/components/schemas/SearchResult'

    SearchResult:
      type: object
      properties:
        code:
          type: string
        title:
          type: string
        date_start:
          type: integer
        date_end:
          type: integer

    TableVariables:
      type: object
      description: Variables available for a specific table.
      properties:
        variable_name:
          type: object
          description: The structure of each variable.
          additionalProperties: 
            type: object
            properties:
              text:
                type: string
              values:
                type: object
                additionalProperties:
                  type: string

    TableData:
      type: string
      description: >
        A string representing CSV formatted data. The first row of the CSV 
        contains the column headers, which correspond to the variables from the query.
```



File: C:\Users\Admin\Documents\StatChat-GPT\scripts\api_search.py
```python
import json
import cohere
from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
from functools import lru_cache
import re
import json
import os

co = cohere.Client(os.environ["COHERE_API_KEY"])
ORG_NAME = "rubenselander"  # Organization name on activeloop hub
VECTOR_STORE_NAME = "eurostat"  # Name of vector store on activeloop hub
# TOKEN = os.environ["ACTIVATELOOP_TOKEN"]


vector_store = VectorStore(
    path=f"hub://{ORG_NAME}/{VECTOR_STORE_NAME}",
    runtime={"tensor_db": True},
)


# Potential filter function for vector_store.search
def filter_tokens_fn(x):
    return x["metadata"].data()["value"]["tokens"] < 1000


def cohere_embedding_function(texts, model="embed-multilingual-v3.0"):
    if isinstance(texts, str):
        texts = [texts]

    response = co.embed(texts, model=model, input_type="search_query", truncate="END")
    return response.embeddings


def search_tables(search_string: str, k: int = 10):
    """Performs a search in tables based on the given search string."""
    results = vector_store.search(
        embedding_data=search_string,
        embedding_function=cohere_embedding_function,
        exec_option="tensor_db",
        return_tensors=["text", "code", "start_date", "end_date"],
        k=k,
    )
    return results


def get_variables(table_code: str) -> dict:
    """Gets the variables for a given table."""
    # select "variables" where "code" == 'HSW_MI03'
    variables = vector_store.search(
        query=f"select variables where code == '{table_code.upper()}'",
        exec_option="tensor_db",
    )
    variables = variables["variables"]
    if variables and isinstance(variables, list) and len(variables) == 1:
        variables = variables[0]
    return variables


def format_search_results(search_results: dict, include_score: bool = False) -> dict:
    """Formats the search results to the format expected by the frontend."""
    if not include_score:
        search_results.pop("score", None)
    formatted_results = []
    # number of results is equal to the length of any of the lists in the dict
    # set the number of results to the length of the FIRST list in the dict
    nbr_of_results = len(list(search_results.values())[0])
    # each dict in the formatted_results list should have all the same keys
    # as the search_results dict

    for i in range(nbr_of_results):
        result = {}
        for key, value in search_results.items():
            if isinstance(value[i], list) and len(value[i]) == 1:
                result[key] = value[i][0]
            else:
                result[key] = value[i]
        formatted_results.append(result)

    return formatted_results


def search_eurostat(search_string: str, year: int = None, k=10) -> dict:
    """Performs a search in Eurostat based on the given search string."""
    search_results = search_tables(search_string, k=k)
    # possible reranking is done here
    # RERANK
    formatted_results = format_search_results(search_results)
    return formatted_results


def test_search():
    search_string = "Does life expectancy in the EU correlate with GDP per capita?"
    search_results = search_eurostat(search_string, k=2)
    print(f"type: {type(search_results)}")

    with open("search_test.json", "w") as f:
        json.dump(search_results, f, indent=4, ensure_ascii=False)


def test_variables():
    table_code = "HSW_MI03"
    variables = get_variables(table_code)
    print(f"variables: {variables}")
    if isinstance(variables, str):
        variables = json.loads(variables)

    # save to variables_test.json
    with open("variables_test.json", "w", encoding="utf-8") as f:
        json.dump(variables, f, indent=4, ensure_ascii=False)


# if __name__ == "__main__":
#     test()
#     test_variables()

```



File: C:\Users\Admin\Documents\StatChat-GPT\scripts\data_retriever.py
```python
import requests
import time
import json
import logging
import pandas as pd
from pyjstat import pyjstat
from io import StringIO


BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{TABLE_CODE}?format=JSON{SELECTIONS}&lang=en"


def build_url(table_code: str, query: dict) -> str:
    """
    Builds a URL to retrieve data from a table based on the given query.
    :param table_code: The code of the table to retrieve data from.
    :param query: The query to use to retrieve data.
    :return: The URL to retrieve data from.
    """
    selections = ""
    for key, values_list in query.items():
        if "*" in values_list:
            continue
        for value in values_list:
            selections += f"&{key}={value}"

    return BASE_URL.format(TABLE_CODE=table_code, SELECTIONS=selections)


def get_response_with_retry(
    url: str, max_attempts: int = 3, timeout: int = 120, raise_exception: bool = False
) -> requests.Response:
    """
    Retrieves a response from a URL with multiple retry attempts.
    :param url: The URL to retrieve a response
    :param max_attempts: The maximum number of attempts to make.
    :return: The response object from the requests library.
    """

    def exponential_backoff(attempt: int):
        time.sleep(2 ** max(0, attempt - 1))

    def _get_response(url: str, attempts: int = 0) -> requests.Response:
        if attempts > max_attempts:
            if raise_exception:
                raise Exception(f"Error retrieving response from '{url}'")
            else:
                return None
        try:
            response = requests.get(url, timeout=timeout)
        except requests.exceptions.Timeout:
            logging.warning(f"Timeout on request to '{url}'")
            return _get_response(url, attempts + 1)
        except Exception as e:
            logging.warning(f"Error retrieving response from '{url}'. Error: {e}")
            return _get_response(url, attempts + 1)

        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            if attempts < max_attempts:
                exponential_backoff(attempts)
            return _get_response(url, attempts + 1)
        else:
            logging.warning(
                f"Error retrieving response from '{url}'. Not a timeout or 429, will not be retried. Status code: {response.status_code}. Text: {response.text}"
            )
            if raise_exception:
                raise Exception(
                    f"Error retrieving response from '{url}'. Status code: {response.status_code}. Text: {response.text}"
                )
            else:
                return None

    return _get_response(url)


def json_stat_to_df(jsonData):
    if not isinstance(jsonData, str):
        try:
            jsonData = json.dumps(jsonData, ensure_ascii=False)
        except:
            jsonData = f"{jsonData}"

    ds = pyjstat.Dataset.read(jsonData)
    df = ds.write("dataframe")
    return df


def dataframe_to_csv_string(df):
    """
    Convert a pandas DataFrame to a CSV string without including the index.

    Parameters:
    - df: pandas.DataFrame

    Returns:
    - str: A string containing the CSV representation of the DataFrame.
    """
    csv_buffer = StringIO()  # Use StringIO to create an in-memory buffer
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()


def get_data(table_code: str, query: dict) -> str:
    """
    Retrieves data from a table based on the given query.
    :param table_code: The code of the table to retrieve data from.
    :param query: The query to use to retrieve data.
    :return: A CSV string containing the data from the table.
    """
    url = build_url(table_code, query)
    response = get_response_with_retry(url, raise_exception=True)
    df = json_stat_to_df(response.text)
    csv_string = dataframe_to_csv_string(df)
    return csv_string

```



File: C:\Users\Admin\Documents\StatChat-GPT\scripts\eurostat_scraper.py
```python
import re
import requests
import gzip
import time
import json
import os
import logging
import concurrent.futures


# WORKFLOW
# 1. Get all dataset codes
# 2.1. Remove potential existing dataset codes (if the script was interrupted before)
# 2.2. Remove existing invalid lines from jsonl file (if the script was interrupted there might be invalid lines)
# 3. Get dataset data for each dataset code
# 4. Format dataset data
# 5. Save dataset data to jsonl file (one dataset per line)

logging.basicConfig(
    filename="eurostat_scraper.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

DATASET_CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/dataflow/all?format=JSON&compressed=true"
BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/DATASET_CODE?format=JSON&lang=EN&compressed=true"
JSONL_SAVE_PATH = "eurostat.jsonl"

# Global variables used to track progress
SCRAPED_DATASETS_COUNT = 0
TOTAL_DATASETS_COUNT = 0


def load_jsonl(file_path):
    """
    Read a JSONL file and return the data as a list of dictionaries.
    """
    output = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            try:
                output.append(json.loads(line))
            except Exception as e:
                logging.error(f"Error loading line: {e}")
                logging.error(line)
                continue
    return output


# Input could be dictionary or list of dictionaries
def append_to_jsonl_file(file_path: str, data: dict | list[dict]):
    """
    Append a dictionary to a JSONL file.
    param file_path: The path to the JSONL file.
    param data: The data to append to the file. Dictionary or list of dictionaries.
    """
    if not os.path.isfile(file_path):
        logging.info(f"Creating new file '{file_path}'...")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("")
    try:
        if isinstance(data, dict):
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(json.dumps(data, ensure_ascii=False) + "\n")
        elif isinstance(data, list):
            with open(file_path, "a", encoding="utf-8") as file:
                for line in data:
                    file.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.error(f"Error appending to file '{file_path}': {e}")
        logging.error(data)
        raise e


# Used to remove invalid lines from the JSONL file. If our script is interrupted, the JSONL file might contain invalid lines.
def remove_invalid_jsonl_lines(file_path: str) -> None:
    """
    Removes invalid lines from a JSONL file. If our script is interrupted, the JSONL file might contain invalid lines.
    :param file_path: The path to the JSONL file.
    """
    logging.info(f"Removing invalid lines from '{file_path}'...")
    valid_dicts = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            try:
                valid_dicts.append(json.loads(line))
            except Exception as e:
                logging.error(f"Error loading line: {e}")
                logging.error(line)
                continue

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("")

    append_to_jsonl_file(file_path, valid_dicts)


def get_existing_dataset_codes(jsonl_path: str = JSONL_SAVE_PATH) -> list[str]:
    """
    Retrieves the dataset codes of all datasets that have already been scraped.
    :param jsonl_path: The path to the JSONL file.
    :return: A list of dataset codes.
    """
    dataset_codes = []
    datasets = load_jsonl(jsonl_path)
    for dataset in datasets:
        if "code" in dataset:
            dataset_codes.append(dataset["code"])

    return dataset_codes


def get_response_with_retry(url: str, max_attempts: int = 3) -> requests.Response:
    """
    Retrieves a response from a URL with multiple retry attempts.
    :param url: The URL to retrieve a response
    :param max_attempts: The maximum number of attempts to make.
    :return: The response object from the requests library.
    """

    def exponential_backoff(attempts: int) -> float:
        # Configured so that max_attempts always results in a 30 second sleep time
        sleep_time = 30 / (2 ** (max_attempts - attempts))
        time.sleep(sleep_time)

    def _get_response(url: str, attempts: int = 0) -> requests.Response:
        response = requests.get(url, timeout=120)
        if response.status_code == 200:
            return response
        elif attempts <= max_attempts:
            if response.status_code == 429:
                exponential_backoff(attempts)
            else:
                time.sleep(3)
            return _get_response(url, attempts + 1)
        else:
            # return None
            raise Exception(
                f"Error retrieving response from '{url}'.\nCode: {response.status_code}\nText: {response.text}"
            )

    return _get_response(url)


# Updated function to extract the first instance of a 4-digit integer from the date string
def extract_year(date_str):
    """Extracts the first instance of a 4-digit integer from the date string."""
    match = re.search(r"\d{4}", date_str)
    return int(match.group()) if match else None


# Updated function to transform variables into a dictionary
def transform_variables(variables):
    """Transforms the 'variables' list into a dictionary as specified."""
    return {
        item["code"]: {"text": item["text"], "values": item["values"]}
        for item in variables
    }


def format_dataset_data(data: dict) -> dict:
    """
    Converts eurostat dataset dictionary to the format used in our deeplake dataset.
    :param dataset_data: The eurostat dataset dictionary.
    :return: Formatted dataset dictionary.
    """
    output_dict = {}
    output_dict["code"] = data["extension"]["id"]
    output_dict["source"] = data["source"]
    output_dict["title"] = data["label"]

    for anno in data["extension"]["annotation"]:
        if anno["type"] == "OBS_PERIOD_OVERALL_LATEST":
            output_dict["end_date"] = extract_year(anno["title"])
        if anno["type"] == "OBS_PERIOD_OVERALL_OLDEST":
            output_dict["start_date"] = extract_year(anno["title"])

    # if start_date or end_date is missing or any of them are None, return None
    if not output_dict.get("start_date", None) or not output_dict.get("end_date", None):
        return None

    variables = []
    var_codes = list(data["dimension"].keys())
    for var_code in var_codes:
        var = data["dimension"][var_code]
        var_dict = {
            "code": var_code,
            "text": var["label"],
            "values": var["category"]["label"],
        }
        variables.append(var_dict)

    output_dict["variables"] = transform_variables(variables)

    return output_dict


def get_dataset_data(dataset_code: str) -> dict:
    """
    Retrieves and returns the data for a dataset.
    :param dataset_code: The code of the dataset to retrieve.
    :return: The data for the dataset.
    """
    logging.info(f"Getting data for dataset '{dataset_code}'...")
    url = BASE_URL.replace("DATASET_CODE", dataset_code)
    response = get_response_with_retry(url)

    if response is None:
        return None
    response_str = gzip.decompress(response.content).decode("utf-8")
    data = json.loads(response_str)
    formatted_data = format_dataset_data(data)
    return formatted_data


def get_dataset_codes() -> list[str]:
    """
    Retrieves and returns a list of all eurostat dataset codes.
    :return: A list of all dataset codes.
    """
    dataset_codes = []

    response = get_response_with_retry(DATASET_CODES_URL)
    response_str = gzip.decompress(response.content).decode("utf-8")
    response_dict = json.loads(response_str)
    for dataset in response_dict["link"]["item"]:
        code = dataset["extension"]["id"]
        dataset_codes.append(code)
    # get existing dataset codes
    existing_dataset_codes = get_existing_dataset_codes()
    logging.info(f"Found {len(existing_dataset_codes)} existing datasets.")
    # remove existing dataset codes and duplicates
    dataset_codes = list(set(dataset_codes) - set(existing_dataset_codes))
    return dataset_codes


def process_dataset_code(dataset_code: str) -> None:
    """
    Process a single dataset code: retrieve data and insert it into the database.
    :param dataset_code: The dataset code to process.
    """
    try:
        dataset_data = get_dataset_data(dataset_code)
        if dataset_data:
            logging.info(f"Saving dataset '{dataset_code}'...")
            append_to_jsonl_file(JSONL_SAVE_PATH, dataset_data)
        else:
            logging.error(f"Error retrieving dataset '{dataset_code}'.")
    except Exception as e:
        logging.error(f"Error scraping dataset '{dataset_code}': {e}")

    global SCRAPED_DATASETS_COUNT
    SCRAPED_DATASETS_COUNT += 1
    logging.info(f"Progress: {SCRAPED_DATASETS_COUNT}/{TOTAL_DATASETS_COUNT}")


def scrape_eurostat(workers: int = 10) -> None:
    """
    Scrapes all eurostat datasets and their metadata and saves it to a jsonl file (one dataset per line).
    :param workers: The number of worker threads to use.
    """
    global TOTAL_DATASETS_COUNT
    dataset_codes = get_dataset_codes()
    logging.info(f"Retrieving data for {len(dataset_codes)} datasets...")
    TOTAL_DATASETS_COUNT = len(dataset_codes)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(process_dataset_code, dataset_codes)


def main():
    with open("eurostat_scraper.log", "w", encoding="utf-8") as file:
        file.write("")
    if os.path.isfile(JSONL_SAVE_PATH):
        remove_invalid_jsonl_lines(JSONL_SAVE_PATH)
    else:
        with open(JSONL_SAVE_PATH, "w", encoding="utf-8") as file:
            file.write("")
    scrape_eurostat()


if __name__ == "__main__":
    main()

```



File: C:\Users\Admin\Documents\StatChat-GPT\scripts\vector_store_init.py
```python
import json
import cohere
from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
import os

co = cohere.Client(os.environ["COHERE_API_KEY"])
ORG_NAME = "rubenselander"  # Organization name on activeloop hub
VECTOR_STORE_NAME = "eurostat"  # Name of vector store on activeloop hub
TABLES_JSONL_PATH = "eurostat.jsonl"  # Path to jsonl file containing scraped tables


TENSOR_PARAMS = [
    {
        "name": "text",
        "htype": "text",
        "dtype": "str",
        "chunk_compression": "lz4",
    },
    {
        "name": "code",
        "htype": "text",
        "dtype": "str",
        "chunk_compression": "lz4",
    },
    {
        "name": "source",
        "htype": "text",
        "dtype": "str",
        "chunk_compression": "lz4",
    },
    {"name": "embedding", "htype": "embedding", "dtype": "float32"},
    {"name": "start_date", "dtype": "int64", "chunk_compression": "lz4"},
    {"name": "end_date", "dtype": "int64", "chunk_compression": "lz4"},
    {"name": "variables", "htype": "json", "chunk_compression": "lz4"},
]


def cohere_embedding_function(
    texts, model="embed-multilingual-v3.0", input_type="search_document"
):
    if input_type not in ["search_document", "search_query"]:
        raise ValueError(
            f"input_type must be one of ['search_document', 'search_query'], got {input_type}"
        )
    if isinstance(texts, str):
        texts = [texts]
    response = co.embed(
        texts,
        model=model,
        input_type=input_type,
    )
    return response.embeddings


def load_jsonl(file_path):
    """
    Read a JSONL file and return the data as a list of dictionaries.
    """
    output = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            try:
                output.append(json.loads(line))
            except Exception as e:
                print(f"Error loading line: {e}\nLine: {line}")
                continue
    return output


def main():
    vector_store = VectorStore(
        path=f"hub://{ORG_NAME}/{VECTOR_STORE_NAME}",
        runtime={"tensor_db": True},
        ingestion_batch_size=92,  # Cohere has a limit of 92 documents per request
        tensor_params=TENSOR_PARAMS,
        overwrite=True,
    )
    tables = load_jsonl(TABLES_JSONL_PATH)

    variables = [t["variables"] for t in tables]
    start_dates = [t["start_date"] for t in tables]
    end_dates = [t["end_date"] for t in tables]
    codes = [t["code"] for t in tables]
    sources = [t["source"] for t in tables]
    texts = [t["title"] for t in tables]

    vector_store.add(
        text=texts,
        code=codes,
        source=sources,
        embedding_function=cohere_embedding_function,
        embedding_data=texts,
        start_date=start_dates,
        end_date=end_dates,
        variables=variables,
    )


if __name__ == "__main__":
    main()

```



File: C:\Users\Admin\Documents\StatChat-GPT\scripts\__init__.py
```python

```




File: C:\Users\Admin\Documents\StatChat-GPT\ToDo.md
# DONE
- Write a script to scrape table titles and metadata from Eurostat API 
(*See `scripts/eurostat_scraper.py`*)
- Write a script for creating custom deeplake vector store 
(*See `scripts/vector_store_init.py`*)
- Write a script for uploading the scraped data to deeplake 
(*See `scripts/vector_store_init.py`*)
- Implement the local flask api (functions for searching and retrieving data). See steps in "Local API".
(*See `api_search.py` and `data_retriever.py`*)
- Define the OpenAPI spec for the local api. 
(*See `openapi.yaml`*)


# LOCAL API
## Functions
- Search for data. 
    - Input: Search query (string) and filters for period (YYYY)
    - Output: List of dataset titles (strings)
- Get retrieval schema for a dataset
    - Input: Dataset code (string)
    - Output: Retrieval schema (json)
- Retrieve data from a dataset
    - Input: Dataset code (string), retrieval query (json according to retrieval schema)
    - Output: Data (csv or json)


# TODO
- Write the instructions for our GPT to use the local api to find and retrieve data from Eurostat API (very simple just need to get the other parts done first)
- DEMO IS DONE AND SHOULD NOW BE READY TO GO!

# SMALL FIXES
- Change all loading and dumping of json and jsonl data to use encoding="utf-8" and ensure_ascii=False. This to avoid issues with special characters such as in the country name "TR": "T�rkiye"

# Further work
- Write deep memory training data. We need X number of question and dataset title pairs. The questions should be something like "How has the average life expectancy in Finland changed for men and woman since 2000?" title should be something like "Life expectancy by country, gender and year". Note: The titles MUST be real titles from our collection.
- Training data should be split into 2 parts. One for training and one for testing. The testing data should be used to evaluate the performance of the model.

- Make a template allowing users to easily connect their own deeplake instance to a GPT
- Make a prettier version of the workflow diagram (https://app.diagrams.net/)
- Make a diagram showcasing the improved performance of the GPT when using Deep Memory


