import doxypypy
import logging

class Keyword:
    """
    @summary: Class that stores a specific keyword and it's associated information
    """
    word = ""   # The given word
    similarWords = []   # Words that are semantically similar the that word.
    _wordFrequency = 0      # Number of times the "word" occurs (not any similar words)
    _similarWordFrequency = 0   # Instances of "word" and all similar words

    def __init__(self, word):
        self.frequency = 1
        self.word = word

    def wordfrequency(self):
        return self._wordFrequency

    def similarwordfrequency(self):
        return self._similarWordFrequency

    def isinsimilarlist(self, word):
        """
        @summary: # Checks if a given word is in the "similarWords" list
        @param word:
        @type word:
        @return:
        @rtype:
        """

    def determinesimilarity(self, word):
        """
        @summary: Checks if the given word is semantically similar to the main keyword
        @param word:
        @type word:
        @return:
        @rtype:
        """

    def distancetonearest(self, word):
        """
        @summary: distance from main "word" to nearest instance of parameter word
        @param word:
        @type word:
        @return:
        @rtype:
        """

    def distancefromkeywordtonearestkeyword(self, keyword):
        """
        @summary: distance from "word" OR SIMILARKEYWORDS to parameter keyword OR ITS SIMILAR KEYWORDS
        @param word:
        @type word:
        @return:
        @rtype:
        """

    def averagedistanceto(self, word):
        """
        "@summary:  average distanceBetween main "word" and parameter word
        @param word:
        @type word:
        @return:
        @rtype:
        """

    def averagedistancefromkeywordtokeyword(self, keyword):
        """
        @summary: averga distance from "word" OR SIMILAR KEYWORDS to parameter keyword AND ITS SIMILAR KEYWORDS
        @param keyword:
        @type keyword:
        @return:
        @rtype:
        """