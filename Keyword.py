import doxypypy
import logging

class Keyword:
    """
    summary: Stores a specific keyword and it's associated information.
             The constructor accepts the word, type, salience, frequency and keyscore.
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
        """
        :return: the frequency value of a word
        :rtype: int 
         """
        return self.frequency

    def similarwordfrequency(self):
        """
        :return: the frequency of a similar word in a document
        :rtype: int 

        """
        return self._similarWordFrequency

    @classmethod
    def issimilar(self, passedWord):
        """
        summary: determines if the passed keyword is similar to (or exactly the same as) the main word in the class
        
        :param str passedWord: word
        :return: boolean value of True or False
        :rtype: bool
        
        """
        if passedWord == self.word:
            return True

        # TODO: Implement some impressive algorithm here that checks synonyms?



    