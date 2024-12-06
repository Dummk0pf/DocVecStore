import pickle

from typing import Annotated

from fastapi import Query
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from settings.config import Config
from utils.normalize_token import normalize_all
from database.milvus_client import MilvusDBClient
from embeddings.unigram_embeddings import vectorize

router = APIRouter(tags=["document_search"])

@router.get("/search", tags=["document_search"])
def token_search(token: str = Query(min_length=3), page: int = 1, limit: int = 10, filter: str | None = None):

    if (limit * page) <= 16000:
        return JSONResponse(
            content={
                "status": False,
                "message": "limit + offset value must be <= 16000"
            }
        )
    
    client = MilvusDBClient()
    config_instance = Config().get_instance()
    results_as_dict = dict()
    results_as_list = list()
    v_offset = 0
    v_limit = 1000

    normalized_token_list = normalize_all(token).split("_")
    query_vectors = [vectorize(token) for token in normalized_token_list]

    for idx, vector in enumerate(query_vectors):
        try:
            while v_offset + v_limit <= 16000:
                results = client.search(
                    embeddings=[vector],
                    limit=v_limit,
                    offset=v_offset,
                    filter=filter,
                    other_search_params={
                        "radius": 0.9, 
                        "range_filter": 1.0,
                    }
                )
                for result in results[0]:
                    book_name = result["entity"]["book_nm"]
                    page_number = result["entity"]["page_nm"]
                    token = result["entity"]["token"]
                    if (book_name, page_number) not in results_as_dict:
                        results_as_dict[(book_name, page_number)] = set()
                    results_as_dict[(book_name, page_number)].add(token)
                v_offset += v_limit
        except ValueError:
            return JSONResponse(
                status_code=500,
                content={
                    "status": False,
                    "message": "no documents to search for"
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "status": False,
                    "message": f"Error due to {e} while parsing token {normalized_token_list[idx]}"
                }
            )


    for key, value in results_as_dict.items():
        b_name, page_nm = key
        token = ",".join(value)
        pickle_dir = config_instance["PICKLE_DIR"]
        _, page_start, _ = pickle.load(open(f"{pickle_dir}/{b_name}.pkl", "rb"))
        results_as_list.append({
            "book_name": b_name,
            "page_number": int(page_start) + int(page_nm),
            "token": token
        })
    
    limited_results = results_as_list[((page - 1) * limit):(page * limit)]

    return JSONResponse(
        status_code=200,
        content={
            "status": True,
            "message": {
                "n_results": len(limited_results),
                "results": limited_results,
            }
        }
    )