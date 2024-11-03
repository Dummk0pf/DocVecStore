import os

from settings.config import Config
from utils.logger import LogManager
Config(os.environ.get("CONFIG_FILE_PATH"))
LogManager("test")

from datagen import datagen

def init():
    from datagen import initialize
    initialize.reset_collection()
    initialize.init_collection()

def main():
    # files = [
    #     ("CompetitiveProgrammingHandBook.pdf", "CompetitiveProgrammingHandBook.txt", 13, 14)
    # ]
    # datagen.run(files)
    datagen.search(["iostream", "algorithm"])

if __name__ == "__main__":
    main()