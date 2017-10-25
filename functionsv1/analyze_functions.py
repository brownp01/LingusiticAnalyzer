import logging
import os
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import storage
import six

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
    """Detects entities in the text."""

    """implicit call for authentication: currently can't get key from GOOGLE_APPLICATION_CREDENTIALS"""
    #client = language.LanguageServiceClient()

    """Explicit call for authentication: Change file path of json file"""
    client = storage.Client.from_service_account_json('/Users/Paul/Documents/googleNLP.json')

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    # [START migration_analyze_entities]
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    for entity in entities:
        print('=' * 20)
        print(u'{:<16}: {}'.format('name', entity.name))
        print(u'{:<16}: {}'.format('type', entity_type[entity.type]))
        print(u'{:<16}: {}'.format('metadata', entity.metadata))
        print(u'{:<16}: {}'.format('salience', entity.salience))
        #print(u'{:<16}: {}'.format('wikipedia_url',
                                   #entity.metadata.get('wikipedia_url', '-')))
        # [END migration_analyze_entities]
        # [END def_entities_text]

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