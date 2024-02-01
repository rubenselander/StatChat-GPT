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
