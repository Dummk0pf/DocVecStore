import pickle
import numpy as np

from settings.config import Config
from utils.normalize_token import normalize_all, remove_stop_words
from utils.logger import LogManager

logger = LogManager().get_logger()
UNIGRAMS_DICT: dict = dict()
VALID_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyz_"


def init() -> None:
    '''
    unigrams to number dictionary is initialized in this function

    Parameters
    ---------------------------------------------------
    None

    Returns
    ---------------------------------------------------
    None
    '''
    global UNIGRAMS_DICT

    config_dict = Config().get_instance()

    try:    
        with open(config_dict["UNIGRAMS"]["DICT_PATH"], "rb") as b_file:
            UNIGRAMS_DICT = pickle.load(b_file)
    except (FileNotFoundError, Exception) as e:
        logger.error("Unigrams dictionary pickle file not found")
        raise Exception(e)
        

def _unigram_vectorize(normalized_token: str) -> (np.ndarray | None):
    '''
    This method is used to convert a word to a vector using weighted unigram approach, in this approach each letter is given a weight based on its position and then normalized

    Parameters
    ---------------------------------------------------
    `token`: normalized token 

    Returns
    ---------------------------------------------------
    list | None: list of numbers that represent the magnitude in each dimension
    '''

    dimensions = len(VALID_CHARACTERS)
    normalized_vector = np.zeros(dimensions, dtype=np.int64)
    symbol_count = np.zeros(dimensions, dtype=np.int32)
    length_of_normalized_token = len(normalized_token)
    weight = length_of_normalized_token * 8

    for i in range(0, len(normalized_token)):
        try:
            idx = UNIGRAMS_DICT[normalized_token[i]]

            if symbol_count[idx] == 0:
                normalized_vector[idx] += weight
                symbol_count[idx] += 1
            elif symbol_count[idx] < 4:
                normalized_vector[idx] += (8 // (2 << (symbol_count[idx]-1)))
                symbol_count[idx] += 1

            weight -= 8
        except (AttributeError, Exception) as e:
            logger.error(f"Invalid token: {normalized_token} {str(e)}")
            return None

    return normalized_vector

def vectorize(token: str) -> (list | None):
    '''
    Wrapper method for vectorize method

    Parameters
    ---------------------------------------------------
    `token`: normalized token 

    Returns
    ---------------------------------------------------
    list | None: list of numbers that represent the magnitude in each dimension
    '''
    normalized_token = normalize_all(token)
    vectorizable_token = remove_stop_words(normalized_token)
    token_vector: np.ndarray | None = _unigram_vectorize(vectorizable_token)
    vector_magnitude = 1

    if token_vector is None:
        raise ValueError("Vectorization Error")

    with np.errstate(all="raise"):
        try:
            result = np.linalg.norm(token_vector, ord=2)
            vector_magnitude = result if result > 0 else 1
        except (RuntimeWarning, RuntimeError, Exception) as e:
            logger.error(f"{token} cannot be vectorized due to {e}")
            raise ValueError("Vectorization Error")
    
    normalized_vector = [(mag/vector_magnitude) for mag in token_vector]
    
    return normalized_vector

init()