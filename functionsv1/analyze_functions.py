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

