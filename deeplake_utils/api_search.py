from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
from openai import AsyncOpenAI
from dotenv import load_dotenv
from functools import lru_cache
from cohere import AsyncClient
import re
import json

import os
import asyncio

load_dotenv()
vector_store = VectorStore(path="data/px_sv_cohere")
client = AsyncOpenAI()


# Implementing Caching for sanitize_string
@lru_cache(maxsize=None)
def sanitize_string(input_str: str) -> str:
    """Sanitizes and simplifies a string for better comparison."""
    return re.sub(r"[^a-zA-Z0-9]", "", input_str.lower().strip())


# Potential filter function for vector_store.search
def filter_tokens_fn(x):
    return x["metadata"].data()["value"]["tokens"] < 1000


async def cohere_embedding_function(texts, model="embed-multilingual-v3.0"):
    if isinstance(texts, str):
        texts = [texts]
    async with AsyncClient(api_key=os.getenv("COHERE_API_KEY")) as co:
        response = await co.embed(texts, model=model, input_type="search_query", truncate="END")
    return response.embeddings


async def search_tables(search_string: str, k: int = 10):
    """Performs an asynchronous search in tables based on the given search string."""
    embedding = await cohere_embedding_function(search_string)
    results = vector_store.search(embedding=embedding, exec_option="python", k=k)
    return results["metadata"]


async def rerank_tables(query: str, search_results: dict, k: int = 10):
    async with AsyncClient() as co:
        rerank_docs = await co.rerank(
            query=query, documents=search_results, top_n=k, model="rerank-multilingual-v2.0"
        )
    return rerank_docs


async def get_time_range_text(table: dict):
    """Get the time range text for a table."""
    for variable in table["variables"]:
        if variable["type"] == "time":
            return f"""Time period: {variable["values"][0]} - {variable["values"][-1]}."""
    return ""


async def get_rerank_docs(results: list):
    """Get the documents to be used for the rerank operation."""
    docs = []
    for table in results:
        time_range_text = await get_time_range_text(table)
        columns = f'\nColumns:{table["columns"]}\n'
        docs.append(
            {"text": f"""{table["title"]}{columns}{time_range_text}""", "index": results.index(table)}
        )
    return docs


async def process_search_results(search_string, results: dict, k: int):
    """Processes and rerank the results of the search operation."""
    rerank_docs = await get_rerank_docs(results)
    async with AsyncClient(api_key=os.getenv("COHERE_API_KEY")) as co:
        reranked_results = await co.rerank(
            query=search_string, documents=rerank_docs, top_n=k, model="rerank-multilingual-v2.0"
        )

    reranked_results = [
        {"text": doc.document, "score": doc.relevance_score, "index": doc.index}
        for doc in reranked_results.results
    ]

    new_results = []
    for doc in reranked_results:
        results[doc["index"]]["score"] = doc["score"]
        new_results.append(results[doc["index"]])

    return new_results


async def api_search(search_string: str, output_num: int = 10, rerank_num: int = 30):
    """Performs a statistical search asynchronously, optionally converting search string to a title."""
    search_results = await search_tables(search_string, k=rerank_num)
    search_results = await process_search_results(search_string, search_results, k=output_num)

    url_info_dict = {}
    function_output = []

    for result in search_results:
        processed_result = {
            "title": result["title"],
            "columns": result["columns"],
            "time_range": await get_time_range_text(result),
            "url": result["api_url"],
        }
        url_info_dict[result["api_url"]] = result
        function_output.append(processed_result)

    output = {
        "search_results": function_output,
        "url_info_dict": url_info_dict,
    }
    return output


def api_search_sync(search_string: str, output_num: int = 10, rerank_num: int = 30):
    """Performs a statistical search synchronously, optionally converting search string to a title."""
    search_results = asyncio.run(api_search(search_string, output_num, rerank_num))
    return search_results


# import time


# Vilken region har haft den högsta andelen godkända elever i svenska för invandrare (sfi) under 2017?
# Hur många deltagare i åldern 18-25 år deltog i kurser om programmering under 2019?
# Hur många kvinnliga företagare inom IT-sektorn finns det i Sverige?
# Hur vanligt är det med internet mobbning i grundskolan?
# Hur många procent av den svenska befolkningen har tillgång till internet i hemmet?
# Vad är den genomsnittliga arbetstiden per vecka för kvinnor i åldern 35-45?
# Vilken är genomsnittlig BMI för män över 50 år?
# Vilken region hade störst andel personer behöriga till högskolan 2020?
# Hur många personer med utländsk bakgrund bodde i Stockholms 2010 och 2020?
# Vad är den genomsnittliga månadslönen för personer med en teknisk utbildning inom den statliga sektorn?
# Hur många företag i Sverige tillämpar åtgärder för att minska sina koldioxidutsläpp?
# Hur förändrades antalet religiösa friskolor mellan 2000 och 2010?
# Hur mycket vatten använder vi i Sverige?
# Vilken kommun har den högsta andelen barn i förskola?
# Vad var inflationstakten i Sverige under 2020?
# Hur många dagar var den genomsnittliga sjukskrivningen i Sverige under 2019?
# Vilken industri var den största arbetsgivaren i Sverige 2002?
# Vilken region har högst hyror för ettor och tvåor?


# def get_title_and_score(search_results: dict):
#     """Get the title and score of the top result."""
#     info_dict = search_results["url_info_dict"]
#     results = [value for value in info_dict.values()]
#     scores = [((1 - result["score"]) * 100) for result in results]
#     scores = [round(score, 5) for score in scores]
#     titles = [result["title"] for result in results]

#     output = []
#     for i in range(len(scores)):
#         output.append({"title": titles[i], "score": scores[i]})
#     return output


# def print_title_and_score(search_results: dict):
#     """Print the title and score of the top result."""
#     title_scores = get_title_and_score(search_results)
#     for title_score in title_scores:
#         print(json.dumps(title_score, indent=4, ensure_ascii=False))


# def __main__():
#     search_string = "Har det blivit vanligare med tidiga skilsmässor?"
#     search_string = "Vad tjänar en polis i snitt per månad?"
#     search_string = "Hur mycket spenderar en svensk man årligen på mat i genomsnitt?"
#     search_string = "Hur många biologilärare fanns det i gymnasieskolan år 2022?"
#     # search_string = "Hur förändrades antalet religiösa friskolor mellan 2000 och 2010?"
#     start_time = time.time()
#     results = asyncio.run(api_search(search_string, 10, 40))
#     # print(json.dumps(results["search_results"], indent=4, ensure_ascii=False))
#     # print(json.dumps(results["url_info_dict"], indent=4, ensure_ascii=False))
#     print_title_and_score(results)
#     print(f"Time taken: {round(time.time() - start_time, 2)} seconds")


# if __name__ == "__main__":
#     __main__()
