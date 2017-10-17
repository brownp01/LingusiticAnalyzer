import logging
import os

LOG_FILE_PATH = 'logging/Linguistic_Analyzer.log'


def printtext(text):
    print(text)


def declarelogger():
    if os.path.isfile(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)
    logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG)
    logging.info("API started")


def identifykeywords(text):
    """
    @summary: returns a list of keyword objects
    @param text:
    @type text:
    @return:
    @rtype:
    """
    return []


def isgarbageword(word):
    """
    @summary: determines if the given word is a garbage word
    @param word:
    @type word:
    @return:
    @rtype:
    """


def removegarbagewords(text):
    """
    @param text: text of document
    @type text: string
    @return: document's text without garbage words (a, I, the, it's)
    @rtype: string
    """

def wordsapi_getsynonym(word):
    """
    @summary: This function calls to the wordsAPI "Synonym" endpoint docs: https://market.mashape.com/wordsapi/wordsapi
    @param word: word to find synonyms of
    @type word: string
    @return: words that are synonymous with the parameter word
    @rtype: list of strings
    """
    # TODO: CHANGE THIS DOCUMENT KEY BEFORE PROJECT GETS HANDED TO MEDTRONIC - NO ACCOUNT CURRENTLY
    apikey = ''
    url = 'https://wordsapiv1.p.mashape.com/words/{word}/synonyms'

def wordsapi_getsimilar(word):
    """
    @summary: This function calls to the wordsAPI "Similar" endpoint docs: https://market.mashape.com/wordsapi/wordsapi
    @param word: word to find similar words of
    @type word: string
    @return: all the words that are similar to the word parameter
    @rtype: list of string
    """
    # TODO: CHANGE THIS DOCUMENT KEY BEFORE PROJECT GETS HANDED TO MEDTRONIC - NO ACCOUNT CURRENTLY
    apikey = ''
    url = 'https://wordsapiv1.p.mashape.com/words/{word}/similar'