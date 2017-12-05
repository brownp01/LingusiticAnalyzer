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
from collections import Counter

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


def identifykeywords(file_text):
    """
    @param file_text: text of document
    @type file_text: list of strings
    @return: KeywordList object
    @rtype: string
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
            # print('=' * 20)
            # print(u'{:<16}: {}'.format('name', entity.name))
            # print(u'{:<16}: {}'.format('type', entity_type[entity.type]))
            # print(u'{:<16}: {}'.format('metadata', entity.metadata))
            # print(u'{:<16}: {}'.format('salience', entity.salience))
            #print(u'{:<16}: {}'.format('wikipedia_url',
                                       #entity.metadata.get('wikipedia_url', '-')))
            # [END migration_analyze_entities]
            # [END def_entities_text]
            keyword_list.insertkeyword(common_functions.createkeywordfromgoogleapientity(entity, file_text))

    return keyword_list

def identifykeywordswithsentiment(file_text):
    """
    @param file_text: text of document
    @type file_text: list of strings
    @return: KeywordList object
    @rtype: string
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

    for i in range(0, len(file_text)):

        if isinstance(file_text[i], six.binary_type):
            file_text[i] = file_text[i].decode('utf-8')

            # Instantiates a plain text document.
            # [START migration_analyze_entities]
        document = types.Document(
            content=file_text[i].encode('utf-8'),
            type=enums.Document.Type.PLAIN_TEXT)

        # Detect and send native Python encoding to receive correct word offsets.
        encoding = enums.EncodingType.UTF32
        if sys.maxunicode == 65535:
            encoding = enums.EncodingType.UTF16

        result = client.analyze_entity_sentiment(document, encoding)

        for entity in result.entities:
            print('Mentions: ')
            print(u'Name: "{}"'.format(entity.name))
            for mention in entity.mentions:
                print(u'  Begin Offset : {}'.format(mention.text.begin_offset))
                print(u'  Content : {}'.format(mention.text.content))
                print(u'  Magnitude : {}'.format(mention.sentiment.magnitude))
                print(u'  Sentiment : {}'.format(mention.sentiment.score))
                print(u'  Type : {}'.format(mention.type))
            print(u'Salience: {}'.format(entity.salience))
            print(u'Sentiment: {}\n'.format(entity.sentiment))

            keyword_list.insertkeyword(common_functions.createkeywordfromgoogleapientity(entity, file_text))

    return keyword_list

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

def getwordfrequency(word, file_text):
    """
    @summary: determines frequency of the given word in the file's text
    @param word: word to find freq. of
    @type word: string
    @param file_text: text of entire file
    @type file_text: list of string
    @return:
    @rtype:
    """
    # TODO: Only populate longlongfiletext once, it is very inefficient the way it is now.
    longlongfiletext = common_functions.stringlisttolonglongstring(file_text).replace('\n', '')
    test = longlongfiletext.count(word)
    return longlongfiletext.count(word)


def calculatescores(kw_list, file_text):
    for kw in kw_list.list:
        kw.keywordscore = calculatekeywordscore(kw_list, file_text, kw)

        # TODO: Get this to work properly
        # kw.yuleskscore = calculateyuleskscore(kw_list, file_text, kw)


def calculatekeywordscore(kw_list, file_text, kw):
    """
    @summary: calculate a keyword score for a single keyword
    @param kw_list: all keywords
    @type kw_list: list of keywords
    @param file_text: file's entire text
    @type file_text: list of strings
    @param kw: keyword
    @type kw: Keyword
    @return: keyword score
    @rtype: float
    """
    kwscore = float(((kw.salience * kw.frequency)/len(kw_list.list)) * 1000)
    return kwscore


# TODO: Get this to work properly
def calculateyuleskscore(keyword_list, file_text, kw):

    long_file_text = common_functions.stringlisttolonglongstring(file_text)

    token_counter = collections.Counter(kw.word.upper() for _ in keyword_list)
    m1 = kw.frequency  # sum(token_counter.values())
    m2 = sum([freq ** 2 for freq in token_counter.values()])
    try:
        i = (m1 * m1) / (m2 - m1)
        k = 10000 / i
        return k
    except ZeroDivisionError as e:
        logging.warning("Error: division by zero. Yule's algorithm not completed. Returning -1.")
        return -1


def calculatecomparisonscore(kw_list, reg_kw_list):
    """
    @summary: Compares the calculated scores of the two documents
    @param kw_list:
    @type kw_list: KeywordList
    @param reg_kw_list:
    @type reg_kw_list: KeywordList
    @return:
    @rtype:
    """
    # This is rudimentary, but actually does a decent job at comparing two documents
    return round(100 - abs(kw_list.avgkeywordscore - reg_kw_list.avgkeywordscore),2)
