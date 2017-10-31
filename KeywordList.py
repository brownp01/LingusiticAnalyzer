class KeywordList:
    list = [] # List of keyword objects
    uniquekeywords = 0

    def __init__(self):
        self.list = []
        self.uniquekeywords = 0

    @staticmethod
    def insertkeyword(self, keyword):
        """
        @summary:
        @param keyword: an instance of the class Keyword
        @type keyword:
        @return:
        @rtype:
        """

        # Check "similar words" lists

        if not self.existsinlist(self, keyword.word):
            list.append(keyword)
            self.uniquekeywords += 1


    @staticmethod
    def existsinlist(self, keyword_name):
        """
        @summary: searches through the list of keywords and sees if any keywords shares the same Keyword.word
        @param keyword_name:
        @type keyword_name:
        @return: returns true if a keyword with keyword_name as Keyword.word exists in the list. False otherwise.
        @rtype: bool
        """
        for i in range(0, len(list)):
            if list[i].word == keyword_name:
                return True
        return False
