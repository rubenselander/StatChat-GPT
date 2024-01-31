from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
import openai
import os
import json

# title = "px_tables"
file_path = "data/processed_tables/processed_tables.json"
# local_path = f"cache/{title}"
# vector_store_path = f"hub://rubenselander/{title}"


vector_store_path = "hub://rubenselander/tensor_tables"


def embedding_function(texts, model="text-embedding-ada-002"):
    if isinstance(texts, str):
        texts = [texts]
    texts = [t.replace("\n", " ") for t in texts]
    return [
        data["embedding"]
        for data in openai.Embedding.create(input=texts, model=model)["data"]
    ]


with open(file_path, "r", encoding="utf-8") as f:
    tables = json.load(f)

titles = [t["title"] for t in tables]
metadatas = []
for t in tables:
    metadata = {
        "title": t["title"],
        "url": t["url"],
        "variables": t["variables"],
        "ids": t["ids"],
        "texts": t["texts"],
        "tokens": t["valueText_tokens"],
        "source": "Statistics Sweden",
    }
    metadatas.append(metadata)


vector_store = VectorStore(path=vector_store_path, runtime={"tensor_db": True})

# local_vector_store = VectorStore(
#     path=local_path,
# )


vector_store.add(
    text=titles,
    embedding_function=embedding_function,
    embedding_data=titles,
    metadata=metadatas,
)

local_vector_store.add(
    text=titles,
    embedding_function=embedding_function,
    embedding_data=titles,
    metadata=metadatas,
)
