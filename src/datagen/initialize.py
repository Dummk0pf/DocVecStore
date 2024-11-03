import os

from settings.config import Config
from utils.logger import LogManager
from database.milvus_client import MilvusDBClient

Config(os.environ.get("CONFIG_FILE_PATH"))
LogManager("test")
config_dict = Config().get_instance()

def reset_database():
    db_client = MilvusDBClient()
    db_client.delete_database(config_dict["MILVUS"]["DB"])

def reset_collection():
    db_client = MilvusDBClient()
    db_client.delete_collection(config_dict["MILVUS"]["TEST_COLLECTION"])

def init_database():
    db_client = MilvusDBClient()
    print(db_client.list_all_databases())
    db_client.create_database(config_dict["MILVUS"]["DB"])
    print(db_client.list_all_databases())

def init_collection():
    db_client = MilvusDBClient()
    print(db_client.list_all_collections())
    db_client.create_collection(config_dict["MILVUS"]["TEST_COLLECTION"])
    print(db_client.list_all_collections())