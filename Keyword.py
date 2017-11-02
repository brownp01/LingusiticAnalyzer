import doxypypy
import logging


class Keyword:
    """
    @summary: Class that stores a specific keyword and it's associated information
    """
    word = ""   # The given word
    type = ""   # The type of the word (if it has one)
    metadata = {}   # list of string each of which contain metadata about the given Keyword
    similarWords = []   # Words that are semantically similar the that word.
    frequency = 0
    __score = 0
    _similarWordFrequency = 0   # Instances of "word" and all similar words

    def __init__(self, word):
        self.frequency = 1
        self.word = word

    def __init__(self, nWord, nType):
        self.frequency = 1
        self.word = nWord
        self.type = nType

    def __init__(self, nWord, nType, nFreq):
        self.word = nWord
        self.type = nType
        self.frequency = nFreq

    @classmethod
    def getscore(cls):
        return cls.__score

    @classmethod
    def wordfrequency(self):
        return self.frequency

    @classmethod
    def similarwordfrequency(self):
        return self._similarWordFrequency

    @classmethod
    def processdoctext(self, docTextList):
        """
        @summary: Runs through the list of strings that contain the uploaded document's text and creates a Keyword
        class for each of them
        @param docTextList: the text of the uploaded document
        @type docTextList:  list of string
        @return: list of Keywords
        @rtype: list of Keyword
        """
        keywordList = []

        # for i in range(0, len(docTextList)-1):


    @classmethod
    def isinsimilarlist(self, word):
        """
        @summary: # Checks if a given word is in the "similarWords" list
        @param word:
        @type word:
        @return:
        @rtype:
        """

    @classmethod
    def determinesimilarity(self, word):
        """
        @summary: Checks if the given word is semantically similar to the main keyword
        @param word:
        @type word:
        @return:
        @rtype:
        """

    @classmethod
    def distancetonearest(self, word):
        """
        @summary: distance from main "word" to nearest instance of parameter word
        @param word:
        @type word:
        @return:
        @rtype:
        """

    @classmethod
    def distancefromkeywordtonearestkeyword(self, keyword):
        """
        @summary: distance from "word" OR SIMILARKEYWORDS to parameter keyword OR ITS SIMILAR KEYWORDS
        @param word:
        @type word:
        @return:
        @rtype:
        """

    @classmethod
    def averagedistanceto(self, word):
        """
        "@summary:  average distanceBetween main "word" and parameter word
        @param word:
        @type word:
        @return:
        @rtype:
        """

    @classmethod
    def averagedistancefromkeywordtokeyword(self, keyword):
        """
        @summary: averga distance from "word" OR SIMILAR KEYWORDS to parameter keyword AND ITS SIMILAR KEYWORDS
        @param keyword:
        @type keyword:
        @return:
        @rtype:
        """

    @classmethod
    def issimilar(self, passedWord):
        """
        @summary: determines if the passed keyword is similar to (or exactly the same as) the main word in the class
        @param passedWord: word
        @type passedWord: string
        @return:
        @rtype: bool
        """
        if passedWord == self.word:
            return True

        # TODO: Implement some impressive algorithm here that checks synonyms?
