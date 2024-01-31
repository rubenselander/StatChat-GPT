import json
import cohere as co
import deeplake
from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore


vs_path = "hub://rubenselander/eurostat_vs"
local_vs_path = "eurostat_vs"


def cohere_embedding_function(
    texts, model="embed-multilingual-v3.0", input_type="search_document"
):
    if input_type not in ["search_document", "search_query"]:
        raise ValueError(
            f"input_type must be one of ['search_document', 'search_query'], got {input_type}"
        )
    if isinstance(texts, str):
        texts = [texts]
    response = co.embed(texts, model=model, input_type=input_type, truncate="END")
    return response.embeddings


# Load our data from jsonl file
file_path = "eurostat.jsonl"
ds_title = "eurostat"


vector_store = VectorStore(
    path=vs_path,
    tensor_params=[
        {"name": "image", "htype": "image", "sample_compression": "jpg"},
        {"name": "embedding", "htype": "embedding"},
        {"name": "filename", "htype": "text"},
        {"name": "source", "htype": "text"},
    ],
    runtime={"tensor_db": True},
)
