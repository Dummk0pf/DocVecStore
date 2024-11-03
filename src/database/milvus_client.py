from enum import StrEnum

from pymilvus import DataType, IndexType
from pymilvus import db, MilvusClient, Collection, connections
from pymilvus.exceptions import MilvusException, DataNotMatchException

from settings.config import Config
from utils.singleton import Singleton
from utils.logger import LogManager

logger = LogManager().get_logger()

class Metric(StrEnum):
    INNER_PRODUCT = "IP"
    COSINE_SIMILARITY = "COSINE"
    EUCLIDEAN_DISTANCE = "L2"
    
class Field(StrEnum):
    ID = "id"
    TOKEN = "token"
    PAGE_NM = "page_nm"
    EMBEDDINGS = "embeddings"

class MilvusDBClient(metaclass=Singleton):

    '''
    Client to access MilvusDB
    '''

    def __init__(self) -> None:
        config_dict = Config().get_instance()
        connections.connect(db_name=config_dict["MILVUS"]["DB"], host=config_dict["MILVUS"]["HOST"], port=config_dict["MILVUS"]["PORT"])
        self._client = MilvusClient(uri=f"http://{config_dict['MILVUS']['HOST']}:{config_dict['MILVUS']['PORT']}", db_name=config_dict["MILVUS"]["DB"])
        self._current_collection = config_dict["MILVUS"]["TEST_COLLECTION"]

    @staticmethod
    def create_database(db_name: str) -> None:

        '''
        Utility to create a database
        '''

        try:
            db.create_database(db_name=db_name)
        except Exception:
            logger.error(f"Cannot create database '{db_name}'")
            raise ValueError(f"Cannot create database '{db_name}'")

    @staticmethod
    def list_all_databases() -> list[str]:

        '''
        Utility for returning all the present databases
        '''

        return db.list_database()
    
    @staticmethod
    def delete_database(db_name: str) -> None:

        '''
        Utility for removing a database
        '''

        try:
            db.drop_database(db_name=db_name)
        except Exception:
            logger.error(f"Cannot delete database '{db_name}'")
            raise ValueError(f"Cannot delete database '{db_name}'")
        
    @staticmethod
    def use_database(db_name: str) -> None:

        '''
        Utility for switching the current database
        '''

        try:
            db.using_database(db_name=db_name)
        except Exception:
            logger.error(f"Cannot switch database '{db_name}'")
            raise ValueError(f"Cannot switch database '{db_name}'")
    
    
    def create_collection(self, collection_name: str) -> None:

        '''
        Utility for creating a collection 
        '''

        collection_schema = self._client.create_schema(
            auto_id=True,
            enable_dynamic_field=False,
        )
        
        index_params = self._client.prepare_index_params()
        index_params.add_index(
            field_name=Field.EMBEDDINGS.value,
            index_name="embeddings_index",
            index_type=IndexType.FLAT,
            metric_type=Metric.INNER_PRODUCT.value
        )

        collection_schema.add_field(field_name=Field.ID.value, datatype=DataType.INT64, is_primary=True, auto_id=True)
        collection_schema.add_field(field_name=Field.TOKEN.value, datatype=DataType.VARCHAR, max_length=1600)
        collection_schema.add_field(field_name=Field.PAGE_NM.value, datatype=DataType.INT16)
        collection_schema.add_field(field_name=Field.EMBEDDINGS.value, datatype=DataType.FLOAT_VECTOR, dim=37)  # Change to FLOAT16 if needed

        collection_schema.verify()

        self._client.create_collection(collection_name, schema=collection_schema, index_params=index_params)
        self._current_collection = collection_name

    def use_collection(self, collection_name: str) -> None:

        '''
        Utility for switching the current collection
        '''

        if collection_name in self.list_all_collections():
            self._current_collection = collection_name

        else:
            logger.error(f"Collection '{collection_name}' does not exist and cannot be switched")
            raise ValueError(f"Collection '{collection_name}' does not exist and cannot be switched")

    def delete_collection(self, collection_name: str) -> None:

        '''
        Utility for switching deleting the given collection
        '''

        try:
            self._client.drop_collection(collection_name=collection_name)
        except (MilvusException, Exception) as e:
            logger.error(f"Unable to delete collection {collection_name}")
            raise ValueError(f"Unable to delete collection {collection_name}")

    def list_all_collections(self) -> list[str]:

        '''
        Utility for listing all the collections in the database
        '''

        return self._client.list_collections()

    def load_collection(self) -> None:

        '''
        Utility for loading the collection in memory
        '''

        self._client.load_collection(collection_name=self._current_collection)
        logger.info(f"Collection {self._current_collection} loaded")

    def release_collection(self) -> None:

        '''
        Utility for releasing the collection in memory
        '''

        self._client.release_collection(collection_name=self._current_collection)
        logger.info(f"Collection {self._current_collection} released")

    def count_records_in_collection(self) -> int:

        '''
        Utility for counting the number of records in the collection
        '''

        return Collection(name=self._current_collection).num_entities

    def insert(self, document: dict | list[dict]) -> dict:

        '''
        Utility for single and bulk insert of documents in the current collection

        Parameters
        ---------------------------------------------------
        `document`: dictionary or list of dictionary containing data corresponding to the fields of the collection schema

        Returns
        ---------------------------------------------------
        the unique ids of the documents inserted
        '''

        try:
            return self._client.insert(self._current_collection, document)
        except DataNotMatchException as e:
            logger.error(f"Input Document or list of documents does not match the fields in the collection {self._current_collection}")
            raise ValueError(f"Error occured in insertion of documents due to {e}")
        except (MilvusException, Exception) as e:
            logger.error(f"Error occured in insertion of documents due to {e}")
            raise ValueError(f"Error occured in insertion of documents due to {e}")

    def delete(self, ids: list[int], filter: (str | None) = None) -> dict:

        '''
        Utility for single and bulk deletion of documents in the current collection

        Parameters
        ---------------------------------------------------
        `ids`: list of ids to be deleted
        `filter`: filter clause that will match the documents to be deleted

        Returns
        ---------------------------------------------------
        the unique ids of the documents deleted
        '''

        try:
            return self._client.delete(self._current_collection, ids=ids, filter=filter)
        except (MilvusException, Exception) as e:
            logger.error(f"Error occurred in deletion of documents due to {e}")
            raise ValueError(f"Error occurred in deletion of documents due to {e.message}")

    def search(self, embeddings: (list[list[float]]), filter: str="", output_fields: list[Field]=[Field.TOKEN, Field.PAGE_NM],limit: int = 10, metric_type:Metric = Metric.INNER_PRODUCT, other_search_params: dict = {}):

        '''
        Utility for single and bulk search of documents in the current collection (this type of search only supports single vector fields)
        For multiple vector fields hybrid search must be implemented

        Parameters
        ---------------------------------------------------
        `embeddings`: list of embeddings of the input tokens
        `filter`: filter clause that will match the documents to be searched
        `output_fields`: fields to be included in the output
        `limit`: no of results to be searched
        `metric_type`: distance measuring metric
        `other_search_params`:

            supported_keys:

                * `radius`: float number between (0 and 1)
                * `range_filter`: float number between (0 and 1)
                * `level`: search precision level, possible values are 1, 2, and 3, and defaults to 1. higher values yield more accurate results but slower performance, (This feature currently does not have any effect on the result, but future versions might produce results thus this parameter is also included)
                * `nprobe`: number of units to query during the search (This parameter is only for IVF related indexing, the default indexing (FLAT) does not require this parameter)

            INNER_PRODUCT and COSINE
                to exclude the closest vectors from results, ensure that:
                `radius < distance <= range_filter`
            L2
                to exclude the closest vectors from results, ensure that:
                `range_filter <= distance < radius`

        Returns
        ---------------------------------------------------
        get all the documents that are similar to the input vector embeddings

        '''

        if not isinstance(metric_type, Metric):
            raise ValueError("Must provide a metric type of instance 'Metric'")
        
        if not isinstance(output_fields, list) or any( not isinstance(output_field, Field) for output_field in output_fields):
            raise ValueError("Must provide a output_field of instance list of 'Field'")
        
        output_field_values = [field.value for field in output_fields]

        try:
            return list(self._client.search(self._current_collection, data=embeddings, output_fields=output_field_values, filter=filter, limit=limit, search_params={"metric_type": metric_type.value, "params": other_search_params}))
        except (MilvusException, Exception) as e:
            logger.error(f"Unable to query for the given vector due to {e}")
            raise ValueError(f"Unable to query for the given vector due to {e}")

    def query(self, ids: (int | list[int] | None)=None, filter: str="", output_fields: list[Field]=[Field.TOKEN, Field.PAGE_NM]):

        '''
        Utility for single and bulk query of documents, this is similar to the traditional SQL query of documents

        Parameters
        ---------------------------------------------------
        `ids`: list of ids to be queried
        `filter`: filter clause that will match the documents to be searched
        `output_fields`: fields to be included in the output
    
        Returns
        ---------------------------------------------------
        get all the documents that match the query
        
        '''

        if not isinstance(output_fields, list) or any(not isinstance(output_field, Field) for output_field in output_fields):
            raise ValueError("Must provide a output_field of instance list of 'Field'")
        
        if filter is not None and ids is not None:
            raise ValueError("Both 'filter' and 'id' cannot be provided at the same time")

        output_field_values = [field.value for field in output_fields]

        try:
            return list(self._client.query(self._current_collection, ids=ids, filter=filter, output_fields=output_field_values))
        except (ValueError, MilvusException, Exception) as e:
            logger.error(f"Unable to query for the given vector due to {e}")
            raise ValueError(f"Unable to query for the given vector due to {e}")