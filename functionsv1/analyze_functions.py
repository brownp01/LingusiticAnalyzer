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
    Summary: Declares logger for the current session.
    """
    if not os.path.isfile(LOG_FILE_PATH):
        f = open(LOG_FILE_PATH, 'w+').close()
    logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE_PATH) #filename=LOG_FILE_PATH
    logging.info("API started")

#def isgarbageword(word):
    #"""
    #Summary: Determines if the given word is a "garbage" word that does not contribute to the meaning of the sentence.
    #@param word:
    #@type word:
    #@return:
    #@rtype:
    #"""


def identifykeywords(file_text):
    """
    Summary: Calls the Google NLP API to extract Keyword information from text

    :param str file_text: text of document
    :return: KeywordList object
    :rtype: KeywordList

    """
    """Detects entities in the text."""

    """For use on a local machine: add export API_KEY="your API key" in bash.profile"""
    """for use in AWS: enter API_KEY with key value in configuration settings"""

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
            entities = json.loads(r.text)

            logging.info("Google NLP API entity analysis successful")
            
        except Exception as e:
            logging.info("Google NLP API entity analysis failed")


        for entity in entities['entities']:
            keyword_list.insertkeyword(common_functions.createkeywordfromgoogleapientity(entity, file_text))

    return keyword_list


#def wordsapi_getsynonym(word):
    #"""
    #summary: This function calls to the wordsAPI "Synonym" endpoint docs: https://market.mashape.com/wordsapi/wordsapi
    #@param word: word to find synonyms of
    #@type word: string
    #@return: words that are synonymous with the parameter word
    #@rtype: list of strings
    #"""
    # TODO: CHANGE THIS DOCUMENT KEY BEFORE PROJECT GETS HANDED TO MEDTRONIC - NO ACCOUNT CURRENTLY
    #apikey = ''
    #url = 'https://wordsapiv1.p.mashape.com/words/{word}/synonyms'

#def wordsapi_getsimilar(word):
    #"""
    #@summary: This function calls to the wordsAPI "Similar" endpoint docs: https://market.mashape.com/wordsapi/wordsapi
    #@param word: word to find similar words of
    #@type word: string
    #@return: all the words that are similar to the word parameter
    #@rtype: list of string
    #"""
    # TODO: CHANGE THIS DOCUMENT KEY BEFORE PROJECT GETS HANDED TO MEDTRONIC - NO ACCOUNT CURRENTLY
    #apikey = ''
    #url = 'https://wordsapiv1.p.mashape.com/words/{word}/similar'


def calculatescores(kw_list, file_text):
    """
    Summary: Calculate Yule's k and i scores, and keywords scores for a given document

    :param KeywordList kw_list: list of Keywords
    :param str file_text: Text of file
    :type file_text: List[string]
    :return: void

    """
    for kw in kw_list.list:
        kw.keywordscore = calculatekeywordscore(kw_list, file_text, kw)

        # TODO: Get this to work properly
    yulestuple = calculateyulesscore(file_text)
    kw_list.yuleskscore = yulestuple[0]
    kw_list.yulesiscore = yulestuple[1]


def calculatekeywordscore(kw_list, file_text, kw):
    """
    Summary: calculate a keyword score for a single keyword

    :param KeywordList kw_list: all keywords
    :param file_text: file's entire text
    :type file_text: list[str]
    :param Keyword kw: keyword
    :return: keyword score
    :rtype: float

    """

    kwscore = float(((kw.salience * kw.frequency)/len(kw_list.list)) * 1000)
    return kwscore


# TODO: Get this to work properly
def calculateyulesscore(file_text):
    """
    Summary: calculates Yule's K scores for givven keyword argument
    
    :param file_text: plain text of document
    :type file_text: list[str]
    :return: Yules score of text file
    :rtype: float

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
    Summary: Compares the calculated scores of the two documents and 
             generates value based on that comparison

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
