
class KeywordList:
    list = [] # List of keyword objects
    uniquekeywords = 0
    __keywordscore = 0
    __yuleskscore = 0

    def __init__(self):
        self.list = []
        self.uniquekeywords = 0

    @classmethod
    def getkeywordscore(cls):
        return cls.__keywordscore

    @classmethod
    def getyuleskscore(cls):
        return cls.__yuleskscore

    @classmethod
    def insertkeyword(cls, keyword):
        """
        @summary:
        @param keyword: an instance of the class Keyword
        @type keyword:
        @return:
        @rtype:
        """

        # Check "similar words" lists

        # Check for exact "word"
        if not cls.existsinlist(keyword.word.upper()):
            cls.list.append(keyword)
            cls.uniquekeywords += 1
        else:
            index = cls.getindexofword(keyword.word.upper())
            cls.list[index].frequency += 1


    @classmethod
    def existsinlist(cls, keyword_name):
        """
        @summary: searches through the list of keywords and sees if any keywords shares the same Keyword.word
        @param keyword_name:
        @type keyword_name:
        @return: returns true if a keyword with keyword_name as Keyword.word exists in the list. False otherwise.
        @rtype: bool
        """
        for i in range(0, len(cls.list)):
            if cls.list[i].word == keyword_name:
                return True
        return False

    @classmethod
    def getindexofword(cls, keyword_name):
        for i in range(0, len(cls.list)):
            if cls.list[i].word == keyword_name:
                return i
        return -1;