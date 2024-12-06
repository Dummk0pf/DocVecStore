import pickle

from settings.config import Config
from database.milvus_client import Field
from utils.normalize_token import normalize_all
from database.milvus_client import MilvusDBClient
from embeddings.unigram_embeddings import vectorize

# REMOVE_ME
import pandas as pd
from pprint import pprint
from tabulate import tabulate

def search(query: str):
    db_client = MilvusDBClient()
    normalized_query = normalize_all(query)
    query_vectors = [vectorize(token) for token in normalized_query.split("_")]
    results_dict = dict()
    results_list = list()
    config_instance = Config().get_instance()

    for query_vector in query_vectors:
        offset = 0
        limit = 1000
        while offset + limit <= 16000:
            results = db_client.search(
                embeddings=[query_vector],
                output_fields=[Field.TOKEN, Field.PAGE_NM, Field.BOOK_NM],
                limit=limit,
                offset=offset,
                other_search_params={"radius": 0.9, "range_filter": 1.0}
            )
            for result in results[0]:
                '''
                d = {
                    "book_name": result["entity"]["book_nm"],
                    "page_number": result["entity"]["page_nm"],
                    "token": result["entity"]["token"],
                    "distance": result["distance"],
                }
                '''
                book_name = result["entity"]["book_nm"]
                page_number = result["entity"]["page_nm"]
                token = result["entity"]["token"]
                distance = result["distance"]
                if (book_name, page_number) not in results_dict:
                    results_dict[(book_name, page_number)] = set()
                results_dict[(book_name, page_number)].add(token)
            offset += limit

    for key, value in results_dict.items():
        b_name, page_nm = key
        token = ",".join(value)
        pickle_dir = config_instance["PICKLE_DIR"]
        _, page_start, page_end = pickle.load(open(f"{pickle_dir}/{b_name}.pkl", "rb"))
        results_list.append({
            "book_name": b_name,
            "page_number": int(page_start) + int(page_nm),
            "token": token
        })

    dataframe = pd.DataFrame.from_dict(results_list[:10])
    print(tabulate(dataframe, headers='keys', tablefmt='psql', showindex=False))
