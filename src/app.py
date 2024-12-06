import os
import sys

from settings.config import Config
from utils.logger import LogManager
Config(os.environ.get("CONFIG_FILE_PATH"))
LogManager("test")

from datagen import datagen
from fetch import fetch

def init():
    from datagen import initialize
    initialize.reset_collection()
    initialize.init_collection()

def fetch_tokens():
    input_token = "dijstra algorithm"
    print(f"Input Token: {input_token}")
    fetch.search(input_token)


def main():
    init()
    files = [
        ("Competitive Programming HandBook.pdf", "Competitive Programming HandBook.txt", 13, 289),
        ("Art Of Computer Programming.pdf", "Art Of Computer Programming.txt", 23, 487),
    ]
    datagen.run(files)

if __name__ == "__main__":
    fetch_tokens()
