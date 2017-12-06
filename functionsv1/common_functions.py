import os
from werkzeug.utils import secure_filename
import logging
from functionsv1 import common_functions
from functionsv1 import analyze_functions
from Keyword import Keyword
from werkzeug.datastructures import FileStorage
import docx
import string
import io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import Keyword
from KeywordList import KeywordList
from matplotlib import pyplot
import numpy as np


DOWNLOAD_FOLDER = 'downloads/'
REGULATOR_FOLDER = 'RegulatoryDocuments/'

def homeCount():

    returnVal = homeCount.counter
    homeCount.counter += 1
    return returnVal


homeCount.counter = 0


# going to handle all the mess that is in app.py
def interpretfile(file, localuploadfolder):
    """
        @summary: Interprets file passed to API from browser
        @param file: werkzeug filestorage object
        @type file: werkzeug filestorage object
        @param localuploadfolder:
        @type localuploadfolder: string
        @return: keywordlist
        @rtype: KeywordList
        """
    file_text = []

    # -----------GRABBING TEXT FROM FILE----------- #
    if file.filename[-3:] == 'pdf':
        file_text = common_functions.extractpdftext(file, localuploadfolder)
    elif file.filename[-4:] == 'docx':
        file_text = common_functions.extractmicrosoftdocxtext(file)
    # common_functions.printStringList(file_text)

    # -----------IDENTIFYING KEYWORDS----------- #
    keyword_list = analyze_functions.identifykeywords(file_text)


    # -----------CALCULATING VARIOUS SCORES FOR EACH KEYWORD----------- #
    analyze_functions.calculatescores(keyword_list, file_text)
    keyword_list.calculateavgscores()

    # -----------PUTTING KEYWORDS IN FILE----------- #
    common_functions.outputkeywordtotext(keyword_list)

    return keyword_list


def interpretexistingfile(regfilename):
    """
    @summary: Interprets file that exists in "RegulatoryDocuments"
    @param regfilename: name of file without file ending
    @type regfilename: string
    @return: list of kwywords that have been analyzed
    @rtype: KeywordList
    """
    reg_text = common_functions.getregulatorydoctext(regfilename)
    reg_keyword_list = analyze_functions.identifykeywords(reg_text)
    analyze_functions.calculatescores(reg_keyword_list, reg_text)
    reg_keyword_list.calculateavgscores()

    return reg_keyword_list


def getscorepage(kw_list, reg_kw_list):
    f = open("views/score_response.html", "r")
    returnhtml = f.read().replace('#--KEYWORD_SCORE--#', str(kw_list.getavgkeywordscore())). \
        replace('#--YULESK_SCORE--#', str(kw_list.getyuleskscore()))\
        .replace('#--DOCUMENT_SCORE--#', str(kw_list.getdocumentscore()))\
        .replace('#--COMPARISON_SCORE--#', str(analyze_functions.calculatecomparisonscore(kw_list, reg_kw_list))) \
        .replace('#--REG_YULESK_SCORE--#', str(reg_kw_list.getyuleskscore())) \
        .replace('#--YULESI_SCORE--#', str(kw_list.getyulesiscore())) \
        .replace('#--REG_YULESI_SCORE--#', str(reg_kw_list.getyulesiscore()))

    f.close()
    return returnhtml


def geterrorpage(errtext="Unknown Error"):
    # Returns error page
    f = open("views/invalid_upload.html", "r")
    returnhtml = f.read().replace('##ERROR##', errtext)
    f.close()
    return returnhtml


def extractpdftext(file, testdownload_folder = None, RegDoc = False):
    """
    @summary:   extracts Text from PDF document referenced in given file argument
    @param file:    the object containing the file's information
    @type file:     fileStorage
    @return: list containing the text of the PDF
    @rtype: string
    """
    localdownload_folder = ''

    file_text = []
    filename = file.filename

    try:
        # -- This is for testing, do not remove -- #
        if testdownload_folder is None and RegDoc is False:
            localdownload_folder = DOWNLOAD_FOLDER
            savefile(file, localdownload_folder)
        elif testdownload_folder is not None:
            localdownload_folder = testdownload_folder


        # PdfMiner writes an insane amount of logging statements (one per parsed word, it seems).
        # Remove the below line if you would like to see them.
        logging.disable(logging.CRITICAL)
        # ----------This is the PDFMiner.six PDF Reader ----------#
        pages=None
        if not pages:
            pagenums = set()
        else:
            pagenums = set(pages)

        output = io.StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)

        infile = open(localdownload_folder + file.filename, 'rb')
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page)
        infile.close()
        converter.close()
        text = output.getvalue()        # Worry - An incredibly long string may crash our application
        output.close
        # --------End of PDFMiner reading --------#
        logging.disable(logging.NOTSET) # This re-enables logging
        logging.info("PDF file processed")

        file_text = longstringtostringlist(text, 1024)  # Converting long string to list of strings of size 1024

    except FileNotFoundError as fnfe:
        logging.info("**-- ERROR: unable to find file file --**")
        print(fnfe.strerror)
    if testdownload_folder is None and RegDoc is False:       # If this is not a test, remove file
        os.remove(localdownload_folder + filename)  # Removes created file from directory.
    return cleantext(file_text)


def extractmicrosoftdocxtext(file, testdownload_folder=None):
    """
    @param file: doc file
    @type file: werkzeug filestorage
    @param testdownload_folder: path to test upload folder if necessary
    @type testdownload_folder: string
    @return:
    @rtype:
    """
    file_text = []

    try:
        if testdownload_folder is None:
            localdownload_folder = DOWNLOAD_FOLDER
            savefile(file, localdownload_folder)
        else:
            localdownload_folder = testdownload_folder

        doc = docx.Document(localdownload_folder + file.filename)

        for para in doc.paragraphs:
            if len(para.text) != 0:
                file_text.append(para.text.strip('\t'))
    except FileNotFoundError as fnfe:
        logging.info("**-- ERROR: unable to find file file --**")
        print(fnfe.strerror)
    if testdownload_folder is None:
        os.remove(DOWNLOAD_FOLDER + file.filename)  # Removes created file from directory.
    return cleantext(file_text)


def savefile(file, download_folder=None):

    # -- This is for testing, do not remove -- #
    if(download_folder is not None):
        DOWNLOAD_FOLDER = download_folder

    filename = secure_filename(file.filename)

    logging.info('saving file "' + filename + '"')
    file.save(os.path.join(DOWNLOAD_FOLDER, filename))  # saves uploaded files
    logging.info('"' + filename + '" saved')

    logging.info('opening file "' + filename + '"')  # Logging


def outputkeywordtotext(keylist):
    """
    @summary: This function will write keywords from an analyzed document to a .txt file
    @param keylist: KeywordList object containing keywords from analyzed document
    @type object: KeywordList
    @return: void
    """

    # TODO create file using document title of originating keywords
    file = open('Documents/Keywords.txt', 'w')

    for i in range(0, keylist.uniquekeywords):
        word = keylist.list[i].word
        sal = keylist.list[i].salience
        freq = keylist.list[i].frequency
        keyscore = keylist.list[i].keywordscore

        file.write(word + "," + str(sal) + "," + str(freq) + "," + str(keyscore) + "\n")

    file.close()


def extractkeywordfromtxt(file):
    """
    @summary: This function will extract keyword information from .txt file and place into KeywordList object
    @param file: location of .txt file
    @type file: .txt
    @return: void
    """
    keyword_list = KeywordList()
    i = 0

    f = open(file, 'r')
    for line in f:
        line_list = line.split(',')
        word = line_list[i]
        sal = line_list[i+1]
        freq = line_list[i+2]
        keyscore = line_list[i+3]

        # TODO modify input to Keyword Object to fit overall needs
        newKeyword = Keyword.Keyword(word, 0, float(float(sal)), int(freq), float(float(keyscore.rstrip('\n'))))
        keyword_list.insertkeyword(newKeyword)

    f.close()
    return keyword_list


def cleantext(text_list):
    """
    @summary:
    @param textlist: a list of strings to remove strange characters from
    @type textlist:
    @return:
    @rtype:
    """
    printable = set(string.printable)

    for i in range(0, len(text_list)-1):
        text_list[i] = ''.join(filter(lambda x: x in string.printable, text_list[i]))

    return text_list

def printStringList(textList):
    """
    @summary:
    @param textList:
    @type textList:
    @return:
    @rtype:
    """
    for i in range(0, len(textList)):
        print(textList[i])

def longstringtostringlist(longstring, strsize):
    """
    @summary: This functions splits a long string "longstring" into strings of size "strsize" and returns a list of strs
    @param longstring:  long string to parse through
    @type longstring:
    @param strsize: size of strings to populate list with
    @type strsize:  int
    @return:
    @rtype:
    """

    return_list = [longstring[i:i + strsize] for i in range(0, len(longstring), strsize)]
    return return_list

def stringlisttolonglongstring(string_list):
    """
    @summary:
    @param string_list:
    @type string_list:
    @return:
    @rtype:
    """
    long_string = ""
    for i in range(0, len(string_list)):
        long_string += string_list[i].rstrip()
    return long_string

def createkeywordfromgoogleapientitysentiment(entity, file_text):
    """
    @summary: Creates a keyword from a single entity that is returned by the google API
    @param entity: google API response entity
    @type entity: google API response entity
    @return: populated instance of Keyword class
    @rtype: Keyword
    """
    eName = entity.name.upper()
    eType = entity.type
    eFreq = analyze_functions.getwordfrequency(eName, file_text)
    eSent = entity.sentiment.score

    newKeyword = Keyword.Keyword(eName, eType, eFreq, eSent)

    for key, value in entity.metadata.items():
        newKeyword.metadata[key] = value
    return newKeyword


def createkeywordfromgoogleapientity(entity, file_text):
    """
    @summary: Creates a keyword from a single entity that is returned by the google API
    @param entity: google API response entity
    @type entity: google API response entity
    @param file_text: entire file's text
    @type file_text: list of strings
    @return: populated instance of Keyword class
    @rtype: Keyword
    """

    eName = entity.name
    eType = entity.type
    eSal = entity.salience
    eFreq = getwordfrequency(eName, file_text)

    # newKeyword = Keyword.creacreatenewkeyword_overload_1(entity.name.upper(), entity.type, getwordfrequency(entity.name, file_text), entity.salience)
    newKeyword = Keyword.Keyword(eName.upper(), eType, eSal, eFreq, 0)  # the value 0 refers to default keywordscore

    for key, value in entity.metadata.items():
        newKeyword.metadata[key] = value
    return newKeyword


def appendtokeywordlist(kList, newK):
    """
    @summary: Checks for duplicate keywords and etc. etc. before potentially appending keyword to list
    @param kList: list of keywords.
    @type kList:
    @param newK:
    @type newK:
    @return:
    @rtype:
    """


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


def getregulatorydoctext(filename):
    """
    @summary: Looks in the RegulatoryDocuments folder for the file with the given file name
    @param filename: name of file to open
    @type filename: string
    @return: list of string containing text of file
    @rtype: list of string
    """
    try:
        logging.info('opening regulatory document')

        with open(REGULATOR_FOLDER + filename, 'rb') as fp:
            file = FileStorage(fp)

        reg_text = extractpdftext(file, RegDoc=True)
    except FileNotFoundError and ValueError as e:
        logging.error('could not access regulatory document"' + filename + '"')

    # print(reg_text)
    return cleantext(reg_text)


def kwhighestfrequencies(keyword_list):
    """
    @param keyword_list:
    @type keyword_list: list of keywords
    @return: topkeywords
    @rtype: list of highest frequency keywords
    """

    kwlist = list(keyword_list.list)
    topkeywords = []
    topKeywordfreqs = []

    # This loop finds the 10 most common keywords in the keyword_list
    i = 0
    while i < 10 and len(kwlist) > 0:
        topkeywordfreq = max(x.frequency for x in kwlist)
        topKeywordfreqs.append(topkeywordfreq)

        topkeyword = next(kw for kw in kwlist if kw.frequency == topkeywordfreq)
        topkeywords.append(topkeyword)

        kwlist[:] = [x for x in kwlist if x.word != topkeyword.word] # removes the previously added item so it does not get chosen again
        i += 1

    return topkeywords

def kwhighestkeyscores(keyword_list):
    """
    @param keyword_list:
    @type keyword_list: list of keywords
    @return: topkeywords
    @rtype: list of highest keyword scores
    """

    kwlist = list(keyword_list.list)
    topkeywords = []
    topKeywordscores = []

    # This loop finds the 10 highest keyword scores in the keyword_list
    i = 0
    while i < 10 and len(kwlist) > 0:
        topkeywordscore = max(x.keywordscore for x in kwlist)
        topKeywordscores.append(topkeywordscore)

        topkeyword = next(kw for kw in kwlist if kw.keywordscore == topkeywordscore)
        topkeywords.append(topkeyword)

        kwlist[:] = [x for x in kwlist if x.word != topkeyword.word] # removes the previously added item so it does not get chosen again
        i += 1

    return topkeywords


def plothighestfreqkeywords(keyword_list1, keyword_list2, doc1name='doc1', doc2name = 'doc2'):
    """
    @summary: plots salience of most frequenctly used keywords. Pulls KWs from list1, compares against list2
    @param keyword_list1:
    @type keyword_list1: KeywordList
    @param keyword_list2:
    @type keyword_list2: KeywordList
    @param doc1name: name of first document
    @type doc1name: string
    @param doc2name: name of second document
    @type doc2name: string
    """

    # Clearing previous graph just to be safe
    pyplot.clf()

    kwlist1 = common_functions.kwhighestfrequencies(keyword_list1)
    kwlist2 = common_functions.kwhighestfrequencies(keyword_list2)

    d = 0
    y = []
    p = []
    my_xticks = []
    w = 0.3
    for x in range(len(kwlist1)):
        word = kwlist1[x].word
        s = 0
        while s < len(kwlist2):
            if kwlist2[s].word == word:
                my_xtick = word
                my_xticks.append(my_xtick)
                y.append(kwlist1[x].salience)
                p.append(kwlist2[s].salience)
                d += 1
                break
            else:
                s += 1

    if d == 0:
        pyplot.bar(x, y)
        pyplot.clf()
        pyplot.title('NO COMMON KEYWORDS TO PLOT', fontweight='bold')
        pyplot.savefig(DOWNLOAD_FOLDER + 'topkeyword.png')
        return
    x = np.arange(len(my_xticks))
    # colors = np.random.rand(d)
    pyplot.bar(x, y, width=w, align='center', color='blue', label='User doc: "' + doc1name + '"')
    pyplot.bar(x+w, p, width=w, align='center', color='r', label='Regulatory doc: "' + doc2name + '"')
    # pyplot.scatter(x - w, y, color='blue', label='doc1')
    # pyplot.scatter(x, p, color='r', label='doc2')
    # pyplot.plot(x,y)
    # pyplot.plot(x - w, y, color='blue', label='doc1')
    # pyplot.plot(x, p, color='r', label='doc2')
    # pyplot.scatter(x,y,c=colors)
    pyplot.xticks(x + w/2, my_xticks, fontsize=8, color='black', rotation=90)
    pyplot.yticks(fontsize=8)
    pyplot.title('Salience of Most Common Keywords In File', fontweight='bold')
    pyplot.xlabel('Keywords (in order of frequency in uploaded document)', fontsize=10, color='red')
    pyplot.ylabel('Salience', fontsize=10, color='red')
    pyplot.legend()
    pyplot.tight_layout()
    pyplot.savefig(DOWNLOAD_FOLDER + 'topkeyword.png')
    # pyplot.show()


def plotkeywordscores(keyword_list1, keyword_list2, doc1name='doc1', doc2name = 'doc2'):
    """
    @summary: plots keyword score of most frequently used keywords. Pulls KWs from list1, compares against list2
    @param keyword_list1:
    @type keyword_list1: KeywordList
    @param keyword_list2:
    @type keyword_list2: KeywordList
    @param doc1name: name of first document
    @type doc1name: string
    @param doc2name: name of second document
    @type doc2name: string
    """

    # Clearing previous graph just to be safe
    pyplot.clf()

    #kwlist1 = common_functions.kwhighestfrequencies(keyword_list1)
    #kwlist2 = common_functions.kwhighestfrequencies(keyword_list2)
    kwlist1 = common_functions.kwhighestkeyscores(keyword_list1)
    kwlist2 = common_functions.kwhighestkeyscores(keyword_list2)

    d = 0
    y = []
    p = []
    my_xticks = []
    w = 0.3
    for x in range(len(kwlist1)):
        word = kwlist1[x].word
        s = 0
        while s < len(kwlist2):
            if kwlist2[s].word == word:
                my_xtick = word
                my_xticks.append(my_xtick)
                y.append(kwlist1[x].keywordscore)
                p.append(kwlist2[s].keywordscore)
                d += 1
                break
            else:
                s += 1

    if d == 0:
        pyplot.bar(x, y)
        pyplot.clf()
        pyplot.title('NO COMMON KEYWORDS TO PLOT', fontweight='bold')
        pyplot.savefig(DOWNLOAD_FOLDER + 'topkeywordscores.png')
        return
    x = np.arange(len(my_xticks))
    # colors = np.random.rand(d)
    pyplot.bar(x, y, width=w, align='center', color='blue', label='User doc: "' + doc1name + '"')
    pyplot.bar(x+w, p, width=w, align='center', color='r', label='Regulatory doc: "' + doc2name + '"')
    # pyplot.scatter(x - w, y, color='blue', label='doc1')
    # pyplot.scatter(x, p, color='r', label='doc2')
    # pyplot.plot(x,y)
    # pyplot.plot(x - w, y, color='blue', label='doc1')
    # pyplot.plot(x, p, color='r', label='doc2')
    # pyplot.scatter(x,y,c=colors)
    pyplot.xticks(x + w/2, my_xticks, fontsize=8, color='black', rotation=90)
    pyplot.yticks(fontsize=8)
    pyplot.title('Keyword Score of Most Common Keywords In File', fontweight='bold')
    pyplot.xlabel('Keywords (in order of keyword score in uploaded document)', fontsize=10, color='red')
    pyplot.ylabel('Keyword Score', fontsize=10, color='red')
    pyplot.legend()
    pyplot.tight_layout()
    pyplot.savefig(DOWNLOAD_FOLDER + 'topkeywordscores.png')
    # pyplot.show()






