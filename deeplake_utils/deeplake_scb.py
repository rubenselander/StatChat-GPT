from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
import openai
import os
import json


vs = VectorStore(path="hub://rubenselander/px_tables")

# vector_store_path = "cache/t_tables"
os.environ["ACTIVELOOP_TOKEN"] = (
    "eyJhbGciOiJIUzUxMiIsImlhdCI6MTY5NzgzMjY2MiwiZXhwIjoxNzYwOTkxMDQ0fQ.eyJpZCI6InJ1YmVuc2VsYW5kZXIifQ.y1fg-LbYELU_nY4KCuRKPqZJshvw-oUnK7fNyLQw4s6CZHdSjayn8uQ03nJGKn2oh-PFn8PORqSPLwkX82ePNQ"
)

vector_store_path = "cache/px_tables"
vector_store = VectorStore(
    path=vector_store_path,
)


def embedding_function(texts, model="text-embedding-ada-002"):
    if isinstance(texts, str):
        texts = [texts]
    texts = [t.replace("\n", " ") for t in texts]
    return [
        data["embedding"]
        for data in openai.Embedding.create(input=texts, model=model)["data"]
    ]


def search_title(
    input: str, k: int = 4, return_metadata: bool = False, return_score: bool = True
):
    result = vector_store.search(
        embedding_data=input, embedding_function=embedding_function, k=k
    )
    output = []
    for i in range(len(result["id"])):
        entry = {}
        if return_score:
            entry["score"] = result["score"][i]
        entry["title"] = result["metadata"][i]["title"]
        entry["url"] = result["metadata"][i]["url"]
        if return_metadata:
            entry["variables"] = result["metadata"][i]["variables"]
            entry["ids"] = result["metadata"][i]["ids"]
            entry["texts"] = result["metadata"][i]["texts"]
            entry["id"] = result["id"][i]
        output.append(entry)
    return output


def search_tables(
    search_string: str,
    k: int = 5,
    max_tokens: int = 8000,
    return_metadata: bool = False,
    return_score: bool = True,
    return_tokens: bool = False,
):
    max_tokens = max_tokens

    def filter_tokens_fn(x):
        return x["metadata"].data()["value"]["tokens"] < max_tokens

    result = vector_store.search(
        embedding_data=search_string,
        embedding_function=embedding_function,
        filter=filter_tokens_fn,
        exec_option="python",
        k=k,
    )
    output = []
    for i in range(len(result["id"])):
        entry = {
            "title": result["metadata"][i]["title"],
            "url": result["metadata"][i]["url"],
        }
        entry["score"] = result["score"][i]
        if return_tokens:
            entry["tokens"] = result["metadata"][i]["tokens"]
        if return_metadata:
            entry["variables"] = result["metadata"][i]["variables"]
            entry["ids"] = result["metadata"][i]["ids"]
            entry["texts"] = result["metadata"][i]["texts"]
            entry["id"] = result["id"][i]

        output.append(entry)
    output = sorted(output, key=lambda x: x["score"])
    if not return_score:
        for entry in output:
            del entry["score"]
    return output
