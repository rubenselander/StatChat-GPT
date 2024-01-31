from collections import deque
from io import StringIO
import random
import pandas as pd
import requests
import gzip
import time
import json
import os
import logging
import sqlite3
import concurrent.futures


# WORKFLOW
# 1. Get all dataset codes
# 2. Get potential dataset codes from existing data (if the script was interrupted)
# 3. Get dataset data for each dataset code
# 4. Save dataset data to file after each retrieval

logging.basicConfig(
    filename="eurostat_scraper.log",
    level=logging.DEBUG,
)

DATASET_CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/dataflow/all?format=JSON&compressed=true"
BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DATASET_CODE?format=JSON&lang=EN&sinceTimePeriod=2025"
JSONL_SAVE_PATH = "eurostat.jsonl"
# test url: "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/SDG_14_50?format=JSON&lang=EN&compressed=true"


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
            return None

    return _get_response(url)


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
            output_dict["start_date"] = anno["title"]
        if anno["type"] == "OBS_PERIOD_OVERALL_OLDEST":
            output_dict["end_date"] = anno["title"]

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

    output_dict["variables"] = variables

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
    data = response.json()
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


def scrape_eurostat(workers: int = 5) -> None:
    """
    Scrapes all eurostat datasets and their metadata and saves it to a jsonl file (one dataset per line).
    :param workers: The number of worker threads to use.
    """
    dataset_codes = get_dataset_codes()
    logging.info(f"Retrieving data for {len(dataset_codes)} datasets...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(process_dataset_code, dataset_codes)


def main():
    with open("eurostat_scraper.log", "w", encoding="utf-8") as file:
        file.write("")
    with open(JSONL_SAVE_PATH, "w", encoding="utf-8") as file:
        file.write("")
    scrape_eurostat()


if __name__ == "__main__":
    main()
