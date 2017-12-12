import doxypypy
import logging

class Keyword:
    """
    @summary: Class that stores a specific keyword and it's associated information
    """

    def __init__(self, nWord = "", nType = 0, nSal = 0, nFreq = 0, nKeyscore = 0):
        self.word = nWord
        self.type = nType
        self.salience = float(nSal)
        self.frequency = nFreq
        self.keywordscore = float(nKeyscore)
        self.metadata = {}
        self.similarWords = []
        self.yuleskscore = float(0)
        self.yulesiscore = float(0)
        self._similarWordFrequency = 0


    def wordfrequency(self):
        return self.frequency


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
