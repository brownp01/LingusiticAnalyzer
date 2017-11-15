
class KeywordList:

    def __init__(self):
        self.list = []
        self.uniquekeywords = 0
        self.keywordscore = 0
        self.yuleskscore = 0


    def getkeywordscore(self):
        return self.keywordscore


    def getyuleskscore(self):
        return self.yuleskscore


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