import json
import cohere
from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
from functools import lru_cache
import re
import json
import os

co = cohere.Client(os.environ["COHERE_API_KEY"])
ORG_NAME = "rubenselander"  # Organization name on activeloop hub
VECTOR_STORE_NAME = "eurostat_cohere"  # Name of vector store on activeloop hub
# TOKEN = os.environ["ACTIVATELOOP_TOKEN"]


vector_store = VectorStore(
    path=f"hub://{ORG_NAME}/{VECTOR_STORE_NAME}",
    runtime={"tensor_db": True},
)


# # Potential filter function for vector_store.search
# def filter_tokens_fn(x):
#     return x["metadata"].data()["value"]["tokens"] < 1000


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


def format_variable(variable: dict, variable_code: str) -> dict:
    """Formats a variable from the vector store to the format expected by the frontend."""
    formatted_variable = {"code": variable_code, "text": variable["text"], "values": []}
    for value_code, value_text in variable["values"].items():
        formatted_variable["values"].append(
            {
                "code": value_code,
                "text": value_text,
            }
        )
    return formatted_variable


def get_variables(table_code: str) -> list[dict]:
    """Gets the variables for a given table."""
    # select "variables" where "code" == 'HSW_MI03'
    variables = vector_store.search(
        query=f"select variables where code == '{table_code.upper()}'",
        exec_option="tensor_db",
    )
    variables = variables["variables"]
    if variables and isinstance(variables, list) and len(variables) == 1:
        variables = variables[0]

    formatted_variables = []
    for variable_code, variable in variables.items():
        formatted_variables.append(format_variable(variable, variable_code))
    return formatted_variables


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


test_search()
# https://ec.europa.eu/eurostat/databrowser/view/lfsa_upgadl


# def test_variables():
#     table_code = "HSW_MI03"
#     variables = get_variables(table_code)
#     print(f"variables: {variables}")
#     if isinstance(variables, str):
#         variables = json.loads(variables)

#     # save to variables_test.json
#     with open("variables_test.json", "w", encoding="utf-8") as f:
#         json.dump(variables, f, indent=4, ensure_ascii=False)


# if __name__ == "__main__":
#     test()
#     test_variables()
