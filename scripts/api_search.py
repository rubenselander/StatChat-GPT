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
        return_tensors="*",
        k=k,
    )
    return results


# def rerank_tables(query: str, search_results: dict, k: int = 10):
#     rerank_docs = co.rerank(
#         query=query,
#         documents=search_results,
#         top_n=k,
#         model="rerank-multilingual-v2.0",
#     )
#     return rerank_docs


# def get_rerank_docs(results: list):
#     """Get the documents to be used for the rerank operation."""
#     docs = []
#     for table in results:
#         time_range_text = await get_time_range_text(table)
#         columns = f'\nColumns:{table["columns"]}\n'
#         docs.append(
#             {
#                 "text": f"""{table["title"]}{columns}{time_range_text}""",
#                 "index": results.index(table),
#             }
#         )
#     return docs


# def process_search_results(search_string, results: dict, k: int):
#     """Processes and rerank the results of the search operation."""
#     rerank_docs = get_rerank_docs(results)

#     reranked_results = co.rerank(
#         query=search_string,
#         documents=rerank_docs,
#         top_n=k,
#         model="rerank-multilingual-v2.0",
#     )

#     reranked_results = [
#         {"text": doc.document, "score": doc.relevance_score, "index": doc.index}
#         for doc in reranked_results.results
#     ]

#     new_results = []
#     for doc in reranked_results:
#         results[doc["index"]]["score"] = doc["score"]
#         new_results.append(results[doc["index"]])

#     return new_results


def search_eurostat(search_string: str, year: int = None, k=10) -> dict:
    """Performs a search in Eurostat based on the given search string."""
    search_results = search_tables(search_string, k=k)
    return search_results


def test():
    search_string = "Does life expectancy in the EU correlate with GDP per capita?"
    search_results = search_eurostat(search_string, k=2)
    print(f"type: {type(search_results)}")
    # print(f"search_results: \n{search_results}")
    # save to search_test.json
    if isinstance(search_results, str):
        search_results = json.loads(search_results)

    # pop the embedding, id and source fields, the search results obj is a dict
    search_results.pop("embedding")
    search_results.pop("id")
    search_results.pop("source")

    with open("search_test.json", "w") as f:
        json.dump(search_results, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    test()
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
