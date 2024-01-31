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
