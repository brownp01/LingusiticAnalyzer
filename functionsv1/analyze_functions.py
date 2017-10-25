import logging
import os
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from oauth2client.service_account import ServiceAccountCredentials
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

    """implicit call for authentication: add export GOOGLE_APPLICATION_CREDENTIALS= "/path/to/json file" 
        in bash.profile and bash.profile_pysave"""

    client = language.LanguageServiceClient()

    """Explicit call for authentication: Change file path of json file. Authentication is accepted but 
       does not function properly for the Google Language API"""

    #creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/Paul/Documents/googleNLP.json')
    #client = language.LanguageServiceClient(credentials=creds)


    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    # [START migration_analyze_entities]
    # TODO: Issues start here in regards to prepping the text for the API. Run debugger. Without FLASK, code works.
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