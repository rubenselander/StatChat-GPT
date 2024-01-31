import json
import cohere as co
import deeplake


def cohere_embedding_function(
    texts, model="embed-multilingual-v3.0", input_type="search_query"
):
    if isinstance(texts, str):
        texts = [texts]
    response = co.embed(texts, model=model, input_type=input_type, truncate="END")
    return response.embeddings
