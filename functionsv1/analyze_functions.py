import logging
import os
from functionsv1 import common_functions
import six
from KeywordList import KeywordList
import collections
import re
import requests
import json

LOG_FILE_PATH = 'logging/Linguistic_Analyzer.log'
KEY = os.environ.get('API_KEY') #Google NLP API Key stored as an environmental variable.

def declarelogger():
    """
    Summary: Declares logger for the current session. Logging statements are re-directed to a local logging file.
    The logging level is set to DEBUG.

    LOG_FILE_PATH = 'logging/Linguistic_Analyzer.log'

    """
    #if not os.path.isfile(LOG_FILE_PATH):
    f = open(LOG_FILE_PATH, 'w').close()
    logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE_PATH)
    logging.info("API started")


def identifykeywords(file_text):
    """
    Summary: Calls the Google NLP API to extract Keyword information from text. The 'analyze entities' from the API
    is utilized. The information retained from the API is 'entity' (keyword) and the 'salience' value of
    a particular keyword.

    Information regarding the Google NLP API can be found at: https://cloud.google.com/natural-language/

    For use on a local machine: add export API_KEY="your API key" in bash.profile or whichever file contains
    environmental variable setup.

    For use in AWS: enter 'API_KEY' with key value in AWS configuration settings

    *file_text* contains the text of a particular document in a list of strings. The original idea here was concern that
    a long string of text would crash the app due to memory constraints. However, if document text is broken up and sent
    to the API as such, the analysis would not encompass the document in its entirety. Instead, the scores provided would
    be focused on each 'chunk' of text. Therefore, analysis of an entire document would be inaccurate. The list of strings
    idea here has remained, but the 'chunk' size for *file_text* can be configured in /applicationconfig.json. Default settings
    allow for a single string text input of a document into the API.

    For each entity identified by the API, :func:`commonfunctions.createkeywordfromgoogleapientity` is used to extract the information
    from the *entities* dictionary variable and places it into a :class:`Keyword`. The returned Keyword is then placed
    into the :class:`KeywordList` object via :func:`KeywordList.insertkeyword`.

    :param List[str] file_text: text of document
    :return: KeywordList object
    :rtype: KeywordList
    :raises: Exception

    """
    """Detects entities in the text."""

    keyword_list = KeywordList()

    # TODO: Maybe change this to long string? There is a chance that would crash the app with large documents though

    for i in range(0, len(file_text)):

        if isinstance(file_text[i], six.binary_type):
            file_text[i] = file_text[i].decode('utf-8')

        try:
            logging.info("Connecting to Google NLP API Entity Analysis...")

            url = "https://language.googleapis.com/v1/documents:analyzeEntities?key="+KEY
            d= {"encodingType": "UTF8", "document": {"type": "PLAIN_TEXT","content": file_text[i]}}

            r = requests.post(url, json=d)
            entities = json.loads(r.text)   #takes JSON given data from API and puts info into an 'entities' dictionary

            logging.info("Google NLP API entity analysis successful")
            
        except Exception as e:
            logging.info("Google NLP API entity analysis failed")


        for entity in entities['entities']:
            keyword_list.insertkeyword(common_functions.createkeywordfromgoogleapientity(entity, file_text))

    return keyword_list


def calculatescores(kw_list, file_text):
    """
    Summary: function that calls :func:`calculatekeywordscore` and :func:`calculateyulesscore` and inputs those values
    into :class:`Keyword` and :class:`KeywordList` respectively for a particular document.

    :param KeywordList kw_list: list of Keywords
    :param List[str] file_text: Text of file
    :return: void

    """
    logging.info("Calculating scores...")

    for kw in kw_list.list:
        kw.keywordscore = calculatekeywordscore(kw_list, file_text, kw)

        # TODO: Get this to work properly
    yulestuple = calculateyulesscore(file_text)
    kw_list.yuleskscore = yulestuple[0]
    kw_list.yulesiscore = yulestuple[1]

    logging.info("Score calculation complete.")


def calculatekeywordscore(kw_list, kw):
    """
    Summary: calculate a keyword score for a single keyword. The current algorithm utilized is:
    [(keyword salience * keyword frequency) / (total keywords)] * 1000.
    Since the salience and frequency of a particular keyword is important to the overall feel of a document, these values
    are used to calculate the score.

    :param KeywordList kw_list: all Keywords of a document.
    :param Keyword kw: keyword
    :return: keyword score
    :rtype: float

    """

    kwscore = float(((kw.salience * kw.frequency)/len(kw_list.list)) * 1000)
    return kwscore


# TODO: Get this to work properly
def calculateyulesscore(file_text):
    """
    Summary: calculates Yule's K/I scores for a given document. These scores are used to determine the lexical richness
    of a given document.

    This function starts by ensuring that *file_text* is converted into a long string vice a list of strings to ensure
    accurate calculation of the scores. Then, the string is split into tokens via :func:`tokenize`. The Yule's K/I algorithm
    is implemented based on the tokens provided. If there is a *'Division by Zero'* error, an exception will be raised and
    the default score value will be **'-1'**
    
    :param List[str] file_text: plain text of document
    :return: Yules score of text file [Yule's K, Yule's I]
    :rtype: float
    :raises: ZeroDivisionError

    """
    try:
        long_file_text = common_functions.stringlisttolonglongstring(file_text)

        tokens = tokenize(long_file_text)
        token_counter = collections.Counter(tok.upper() for tok in tokens)
        m1 = sum(token_counter.values())
        m2 = sum([freq ** 2 for freq in token_counter.values()])
        i = (m1 * m1) / (m2 - m1)
        k = 10000/i
    except ZeroDivisionError as e:
        logging.warning("Error: division by zero. Yule's algorithm not completed. Returning -1.")
        return -1, -1
    return round(k, 2), round(i, 2)


def calculatecomparisonscore(kw_list, reg_kw_list):
    """
    Summary: Compares the calculated scores of the two documents and generates value based on that comparison.

    1. The top 10 Keywords with the highest frequency is gathered from the user document.
    2. The top 10% of the regulatory document Keywords are gathered.
    3. For the top 10 Keywords in the user document, if they are in the top 10% of words in the regulatory document, a value
       of '1' is added to a variable called *tempscore*.
    4. *tempscore* / top 10% of reg doc keywords = the new *tempscore*
    5. The final score that is returned:
       100 - [abs(average keyword score of user doc - average keyword score of reg doc)] * *tempscore*


    :param KeywordList kw_list: list of Keywords
    :param KeywordList reg_kw_list: list of Keywords
    :return: comparison score of two documents
    :rtype: float


    """

    tempscore = 0.0

    # Get top ten KWs with highest frequencies
    topdockws = list(common_functions.kwhighestfrequencies(kw_list, 10))

    # get top ten percent of regulatory kws
    regkwnum = len(reg_kw_list.list) if len(reg_kw_list.list) * .1 < len(topdockws) else len(reg_kw_list.list) * .1

    topregkws = list(common_functions.kwhighestfrequencies(reg_kw_list, regkwnum))

    # look at top ten keywords in file (by frequency), and for each of them, see if they are in the top 10% of words
    # in reg_doc

    for kw in topdockws:
        for i in range(0, len(topregkws)):
            if kw.word == topregkws[i].word:
                tempscore = tempscore + 1

    tempscore = tempscore/regkwnum



    # This is rudimentary, but actually does a decent job at comparing two documents
    return round((100 - abs(kw_list.avgkeywordscore - reg_kw_list.avgkeywordscore)) * tempscore, 2)


def tokenize(tokenStr):
    """
    Summary: Splits up string into individual tokens.

    :param str tokenStr: a string of words
    :return: tokens
    :rtype: list
    """
    tokens = re.split(r"[^0-9A-Za-z\-'_]+", tokenStr)
    return tokens
