import logging

class KeywordList:

    def __init__(self):
        self.list = []
        self.uniquekeywords = 0
        self.keywordscore = 0
        self.yuleskscore = 0.0
        self.yulesiscore = 0.0
        self.avgkeywordscore = 0
        self.documentscore = 0

    def getdocumentscore(self):
        return self.documentscore

    def getavgkeywordscore(self):
        return self.avgkeywordscore

    def getkeywordscore(self):
        return self.keywordscore

    def getyuleskscore(self):
        return self.yuleskscore

    def getyulesiscore(self):
        return self.yulesiscore

    def calculateavgscores(self):
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

    def insertkeyword(self, keyword):
        """
        @summary:
        @param keyword: an instance of the class Keyword
        @type keyword:
        @return:
        @rtype:
        """

        # Check "similar words" lists

        # Check for exact "word"
        if not self.existsinlist(keyword.word.upper()):
            self.list.append(keyword)
            self.uniquekeywords += 1
        else:
            index = self.getindexofword(keyword.word.upper())
            self.list[index].frequency += 1

    def existsinlist(self, keyword_name):
        """
        @summary: searches through the list of keywords and sees if any keywords shares the same Keyword.word
        @param keyword_name:
        @type keyword_name:
        @return: returns true if a keyword with keyword_name as Keyword.word exists in the list. False otherwise.
        @rtype: bool
        """
        for i in range(0, len(self.list)):
            if self.list[i].word == keyword_name:
                return True
        return False

    def getindexofword(self, keyword_name):
        for i in range(0, len(self.list)):
            if self.list[i].word == keyword_name:
                return i
        return -1
