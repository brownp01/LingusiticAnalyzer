import logging

class KeywordList:
    """
    Summary: A list that contains :class:`Keyword`. *KeywordList* also contains unique keyword value, keyword score,
    Yule's K score, Yule's I score, average keyword score and a document score.

    """

    def __init__(self):
        self.list = []
        self.uniquekeywords = 0
        #self.keywordscore = 0
        self.yuleskscore = 0.0
        self.yulesiscore = 0.0
        self.avgkeywordscore = 0
        self.documentscore = 0

    def getdocumentscore(self):
        """
        Summary: Returns document's score.

        :return: score
        :rtype: int

        """
        return self.documentscore

    def getavgkeywordscore(self):
        """
        Summary: returns document's average keyword score.

        :return: score
        :rtype: int

        """
        return self.avgkeywordscore

    def getkeywordscore(self):
        """
        Summary: returns document's keyword score.

        :return: score
        :rtype: float

        """
        return self.keywordscore

    def getyuleskscore(self):
        """
        Summary: returns document's Yule's I score.

        :return: score
        :rytpe: float

        """
        return self.yuleskscore

    def getyulesiscore(self):
        """
        Summary: returns document's Yule's I score.

        :return: score
        :rtype: float

        """
        return self.yulesiscore

    def calculateavgscores(self):
        """
        Summary: calculates a document's average score values and sets the values in the *KeywordList*

        :return: void
        :raises: ZeroDivisionError

        """
        logging.info("Calculating average scores for document...")
        kwscoresum = float(0)
        yulesksum = float(0)
        yulesisum = float(0)
        try:

            for kw in self.list:
                kwscoresum += kw.keywordscore
                yulesksum += kw.yuleskscore
                yulesisum += kw.yulesiscore

            self.avgkeywordscore = round(kwscoresum / len(self.list),2)
            self.avgyuleskscore = yulesksum / len(self.list)
            self.avgyulesiscore = yulesisum / len(self.list)

        except ZeroDivisionError as zde:
            logging.warning('Division by 0 in "KeywordList.calculateavgscore(). Scores not set')
            self.avgkeywordscore = 0
            self.avgyulesiscore = 0
            self.avgyuleskscore = 0

        logging.info("Average scores for document complete.")

    def insertkeyword(self, keyword):
        """
        Summary: inserts a new :class:`Keyword` into *KeywordList*.

        - A check if the keyword is a letter. If it's a letter, it will not be added to the list.
        - A check if the keyword already exists is handled by :func:`existsinlist`. If it does not exist, the
          :class:`Keyword` is inserted into the list.

        :param Keyword keyword: an instance of the class keyword
        :return: void

        """

        # Check "similar words" lists

        # if single letter, do not insert.
        if len(keyword.word.upper()) == 1:
            return

        # Check for exact "word"
        if not self.existsinlist(keyword.word.upper()):
            self.list.append(keyword)
            self.uniquekeywords += 1


    def existsinlist(self, keyword_name):
        """
        Summary: searches through the list of keywords and sees if any keywords shares the same Keyword.word.
        
        :param str keyword_name: The keyword 
        :return: returns true if a keyword with keyword_name as Keyword.word exists in the list. False otherwise.
        :rtype: bool

        """
        for i in range(0, len(self.list)):
            if self.list[i].word == keyword_name:
                return True
        return False

    def getindexofword(self, keyword_name):
        """
        Summary: returns the index of a :class:`Keyword` in the list of Keywords.

        :param str keyword_name: keyword
        :return: keyword index
        :rtype: int 

        """
        for i in range(0, len(self.list)):
            if self.list[i].word == keyword_name:
                return i

        return -1
