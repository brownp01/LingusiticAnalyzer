import logging
import os
import sys
from google.cloud import language
from google.cloud import language_v1beta2
from google.cloud.language import enums
from google.cloud.language import types
from oauth2client.service_account import ServiceAccountCredentials
from functionsv1 import common_functions
import six
from KeywordList import KeywordList
import collections
import re
from collections import Counter

LOG_FILE_PATH = 'logging/Linguistic_Analyzer.log'


def declarelogger():
    """
    Summary: Declares logger for the current session.
    """
    if os.path.isfile(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)
    logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG)
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
    :rtype: object

    """
    """Detects entities in the text."""

    """implicit call for authentication: add export GOOGLE_APPLICATION_CREDENTIALS= "/path/to/json file" 
        in bash.profile and bash.profile_pysave"""

    keyword_list = KeywordList()

    client = language.LanguageServiceClient()

    """Explicit call for authentication: Change file path of json file. Authentication is accepted but 
       does not function properly for the Google Language API"""
    #creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/Paul/Documents/googleNLP.json')
    #client = language.LanguageServiceClient(credentials=creds)

    # TODO: Maybe change this to long string? There is a chance that would crash the app with large documents though
    for i in range(0, len(file_text)):

        if isinstance(file_text[i], six.binary_type):
            file_text[i] = file_text[i].decode('utf-8')

            # Instantiates a plain text document.
            # [START migration_analyze_entities]
        document = types.Document(
            content=file_text[i],
            type=enums.Document.Type.PLAIN_TEXT)

        # Detects entities in the document. You can also analyze HTML with:
        #   document.type == enums.Document.Type.HTML
        entities = client.analyze_entities(document).entities


        # entity types from enums.Entity.Type
        entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                       'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

        for entity in entities:
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

    :param kw_list: list of Keywords
    :type kw_list: KeywordList
    :param str file_text: Text of file
    :type file_text: List[string]

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

    :param kw_list: all keywords
    :type kw_list: list
    :param file_text: file's entire text
    :type file_text: list of strings
    :param kw: keyword
    :type kw: Keyword
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
    :type file_text: list
    :param kw: Keyword
    :type kw: Keyword

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
        return -1
    return round(k, 2), round(i, 2)


def calculatecomparisonscore(kw_list, reg_kw_list):
    """
    Summary: Compares the calculated scores of the two documents and 
             generates value based on that comparison

    :param kw_list: list of Keywords
    :type kw_list: KeywordList
    :param reg_kw_list: list of Keywords
    :type reg_kw_list: KeywordList

    """
    # This is rudimentary, but actually does a decent job at comparing two documents
    return round(100 - abs(kw_list.avgkeywordscore - reg_kw_list.avgkeywordscore),2)


def tokenize(tokenStr):
    """
    Summary: Splits up string into individual tokens.

    :param tokenStr: a string of words
    :type tokenStr: string
    :return: tokens
    :rtype: list
    """
    tokens = re.split(r"[^0-9A-Za-z\-'_]+", tokenStr)
    return tokens
