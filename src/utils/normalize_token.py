from re import sub
from nltk import download
from unidecode import unidecode
from nltk.corpus import stopwords

STOP_WORDS = set()

GREEK_SMALL_LETTER_TO_WORD = {
    u'\u03B1': 'alpha',
    u'\u03B2': 'beta',
    u'\u03B3': 'gamma',
    u'\u03B4': 'delta',
    u'\u03B5': 'epsilon',
    u'\u03B6': 'zeta',
    u'\u03B7': 'eta',
    u'\u03B8': 'theta',
    u'\u03B9': 'iota',
    u'\u03BA': 'kappa',
    u'\u03BB': 'lamda',
    u'\u03BC': 'mu',
    u'\u03BD': 'nu',
    u'\u03BE': 'xi',
    u'\u03BF': 'omicron',
    u'\u03C0': 'pi',
    u'\u03C1': 'rho',
    u'\u03C3': 'sigma',
    u'\u03C4': 'tau',
    u'\u03C5': 'upsilon',
    u'\u03C6': 'phi',
    u'\u03C7': 'chi',
    u'\u03C8': 'psi',
    u'\u03C9': 'omega',
    u'\u03F5': 'lunate_epsilon',
}

GREEK_CAPITAL_LETTER_TO_WORD = {
    u'\u0391': 'alpha',
    u'\u0392': 'beta',
    u'\u0393': 'gamma',
    u'\u0394': 'delta',
    u'\u0395': 'epsilon',
    u'\u0396': 'zeta',
    u'\u0397': 'eta',
    u'\u0398': 'theta',
    u'\u0399': 'iota',
    u'\u039A': 'kappa',
    u'\u039B': 'lamda',
    u'\u039C': 'mu',
    u'\u039D': 'nu',
    u'\u039E': 'xi',
    u'\u039F': 'omicron',
    u'\u03A0': 'pi',
    u'\u03A1': 'rho',
    u'\u03A3': 'sigma',
    u'\u03A4': 'tau',
    u'\u03A5': 'upsilon',
    u'\u03A6': 'phi',
    u'\u03A7': 'chi',
    u'\u03A8': 'psi',
    u'\u03A9': 'omega',
}

WORD_TO_SMALL_GREEK_LETTER = {
    'alpha': u'\u03B1',
    'beta': u'\u03B2',
    'gamma': u'\u03B3',
    'delta': u'\u03B4',
    'epsilon': u'\u03B5',
    'zeta': u'\u03B6',
    'eta': u'\u03B7',
    'theta': u'\u03B8',
    'iota': u'\u03B9',
    'kappa': u'\u03BA',
    'lamda': u'\u03BB',
    'mu': u'\u03BC',
    'nu': u'\u03BD',
    'xi': u'\u03BE',
    'omicron': u'\u03BF',
    'pi': u'\u03C0',
    'rho': u'\u03C1',
    'sigma': u'\u03C3',
    'tau': u'\u03C4',
    'upsilon': u'\u03C5',
    'phi': u'\u03C6',
    'chi': u'\u03C7',
    'psi': u'\u03C8',
    'omega': u'\u03C9',
    'lunate_epsilon': u'\u03F5',
}

def init() -> None:
    '''
    Initialzes stop words from nltk library and adds custom stop words 
    Initialzes sentence transformer library for performing cosine similarity
    '''

    global STOP_WORDS

    download('stopwords', quiet=True)
    NLTK_STOP_WORDS = set(stopwords.words("english"))
    OTHER_STOPS = set(['other', 'with', 'w', 'unspecified', 'nos'])
    STOP_WORDS = NLTK_STOP_WORDS.union(OTHER_STOPS)

def add_greek_letter(symbol: str, equivalent_word: str, is_small_letter: bool) -> None:

    '''
    Helper function to add a new unicode symbol with its equivalent word to be checked during runtime

    Parameters
    ---------------------------------------
    `symbol`: str -> unicode for the symbol in string format
    `equivalent_word`: str -> equivalent english word for unicode symbol
    `is_small_letter`: str -> add a small letter greek symbol or capital letter

    Returns
    ---------------------------------------
    None
    '''
    
    if is_small_letter:
        if symbol in GREEK_SMALL_LETTER_TO_WORD:
            raise ValueError('Symbol already present')
        normalized_token = normalize_token(equivalent_word)
        GREEK_SMALL_LETTER_TO_WORD[symbol] = normalized_token
        WORD_TO_SMALL_GREEK_LETTER[normalized_token] = symbol
    else:
        if symbol in GREEK_CAPITAL_LETTER_TO_WORD:
            raise ValueError('Symbol already present')
        GREEK_CAPITAL_LETTER_TO_WORD[symbol] = normalize_token(equivalent_word)

def greek_letters(normalized_token: str) -> str:

    '''
    Converts greek characters to english words if they are present as seperate words in the `normalized_token`

    Parameters
    ---------------------------------------
    `normalized_token`: str -> input token that is normalized

    Returns
    ---------------------------------------
    str -> converted string
    '''

    normalized_token_list = normalized_token.split('_')

    for idx, token in enumerate(normalized_token_list):
        if token in GREEK_SMALL_LETTER_TO_WORD:
            normalized_token_list[idx] = GREEK_SMALL_LETTER_TO_WORD[token]
        elif token in GREEK_CAPITAL_LETTER_TO_WORD:
            normalized_token_list[idx] = GREEK_CAPITAL_LETTER_TO_WORD[token]
        
    return '_'.join(normalized_token_list)

def greek_letters_continous(normalized_token: str) -> str:

    '''
    Converts greek characters to english words if they are present in the `normalized_token`

    Parameters
    ---------------------------------------
    `normalized_token`: str -> input token that is normalized

    Returns
    ---------------------------------------
    str -> converted string
    '''

    converted_token = normalized_token

    for character in normalized_token:
        if character in GREEK_SMALL_LETTER_TO_WORD:
            converted_token = converted_token.replace(character, f'_{GREEK_SMALL_LETTER_TO_WORD[character]}_')
        elif character in GREEK_CAPITAL_LETTER_TO_WORD:
            converted_token = converted_token.replace(character, f'_{GREEK_CAPITAL_LETTER_TO_WORD[character]}_')
    
    return replace_multiple_underscores(converted_token)

def words_to_greek_letters(normalized_token: str) -> str:

    '''
    Converts english words to greek characters if they are greek equivalent word and present as seperate words in the `normalized_token`

    Parameters
    ---------------------------------------
    `normalized_token`: str -> input token that is normalized

    Returns
    ---------------------------------------
    str -> converted string
    '''

    normalized_token_list = normalized_token.split('_')
    converted_token_list = [WORD_TO_SMALL_GREEK_LETTER[word] if word in WORD_TO_SMALL_GREEK_LETTER else word for word in normalized_token_list]

    return '_'.join(converted_token_list)

def normalize_token(token_name: str) -> str:

    '''
    Converts all characters from `token_name` to lower case and removes all special characters to underscores

    Parameters
    ---------------------------------------
    `token_name`: str -> input string

    Returns
    ---------------------------------------
    str -> normalized string
    '''

    token_name = token_name.strip().lower()
    pattern = r'[^\w]'
    normalized_token = sub(pattern, '_',token_name)
    return replace_multiple_underscores(normalized_token)

def replace_multiple_underscores(token_name: str) -> str:
    return sub(r'_+', '_', token_name).strip('_')

def remove_stop_words(normalized_token: str) -> str:
    '''
    Removes the custom stop words from the `normalized_token` 

    Parameters
    ---------------------------------------
    `normalized_token`: str -> normalized token 

    Returns
    ---------------------------------------
    str -> stop words removed string
    '''

    normalized_token_list = normalized_token.split('_')
    converted_token_list = [word for word in normalized_token_list if word not in STOP_WORDS]

    return '_'.join(converted_token_list)

def normalize_all(token: str) -> str:
    '''
    Utility method for normalizing tokens with all the normalization methods present in the module
    '''
    
    normalized_token = normalize_token(token)
    normalized_token = greek_letters_continous(normalized_token)
    normalized_token = unidecode(normalized_token, errors='strict')
    normalized_token = remove_stop_words(normalized_token)

    return normalized_token

init()