import yaml
import pathlib

from utils.singleton import Singleton

class Config(metaclass=Singleton):
    def __init__(self, config_file_path = "") -> None:
        config_file_path = pathlib.Path(config_file_path)
        if config_file_path == "" or not config_file_path.exists():
            raise ValueError("provide a valid config file path")
        self.instance = yaml.safe_load(open(config_file_path, "r"))
    
    def get_instance(self):
        return self.instance
