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
import matplotlib
matplotlib.use('agg',warn=False, force=True)
from matplotlib import pyplot
import numpy as np
import datetime
import applicationconfig


DOWNLOAD_FOLDER = 'downloads/'
REGULATOR_FOLDER = 'RegulatoryDocuments/'
DOCUMENTS_FOLDER = 'Documents/'
VIEWS_FOLDER = 'views/'


def homeCount():
    """
        Initializes variables for logging session

        :return: void
    """
    returnVal = homeCount.counter
    homeCount.counter += 1
    return returnVal


homeCount.counter = 0


# going to handle all the mess that is in application.py
def interpretfile(file, localuploadfolder):
    """
        Parses uploaded file's text, identifies keywords, analyzes keywords, and returns a list of Keyword Objects

        :param fileStorage file: file to be interpreted
        :param str localuploadfolder: Place to temporary store file so it can be read from
        :return: list of file's Keywords
        :rtype: KeywordList

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
    Parses, identifies keywords and analyzes content of chosen regulatory file document is being compares against.

    :param str regfilename: name of regulatory file
    :return: list of analyzed Keyword objects
    :rtype: KeywordList

    """
    regfilenamePDF = common_functions.changefileextension(regfilename)
    reg_text = common_functions.getregulatorydoctext(regfilenamePDF)
    #reg_keyword_list = analyze_functions.identifykeywords(reg_text)
    reg_keyword_list = common_functions.extractkeywordfromtxt(regfilename)
    analyze_functions.calculatescores(reg_keyword_list, reg_text)
    reg_keyword_list.calculateavgscores()

    common_functions.outputkeywordtotext(reg_keyword_list, 'Documents/Reg_Keywords.txt')

    return reg_keyword_list


def changefileextension(regfilename):
    """
    Changes the file name string from .txt to .pdf.

    :param str regfilename: name of regulatory file
    :return: string with .pdf file extension
    :rtype: str

    """

    temp = list(regfilename)
    size = len(regfilename)
    temp[size-3] = "p"
    temp[size-2] = "d"
    temp[size-1] = "f"
    regfilenamePDF = "".join(temp)

    return regfilenamePDF


def getscorepage(kw_list, reg_kw_list):
    """
    Returns html page that is populated with proper calculated Keyword, Comparison, and Yule's scores.

    :param KeywordList kw_list: list of user document's Keyword objects
    :param KeywordList reg_kw_list: list of regulatory document's Keywords
    :return: html page with scores displayed
    :rtype: str

    """
    lines = []
    html_str = ''

    logging.info("Begin score page response...")

    with open('Documents/Analytics.txt') as fp:
        line = fp.readline()
        count = 0
        while line and count < 100:
            lines.append(line)
            line = fp.readline()
            count = count + 1

    for l in lines:
        html_str = html_str + '<p>' + l + '</p>'


    #
    # f_ana = open('Documents/Analytics.txt', 'r')
    # analytics_text = f_ana.read()
    # analytics_list = analytics_text.split(';')
    # if analytics_text is not '':
    #     time = analytics_list[0]
    #     calc_time = analytics_list[1]
    #     f_name = analytics_list[2]
    #     f_kws = analytics_list[3]
    #     reg_f_name = analytics_list[4]
    #     reg_f_kws = analytics_list[5]


    f = open("views/score_response.html", "r")
    returnhtml = f.read().replace('#--KEYWORD_SCORE--#', str(kw_list.getavgkeywordscore())). \
        replace('#--YULESK_SCORE--#', str(kw_list.getyuleskscore()))\
        .replace('#--DOCUMENT_SCORE--#', str(kw_list.getdocumentscore()))\
        .replace('#--COMPARISON_SCORE--#', str(analyze_functions.calculatecomparisonscore(kw_list, reg_kw_list))) \
        .replace('#--REG_YULESK_SCORE--#', str(reg_kw_list.getyuleskscore())) \
        .replace('#--YULESI_SCORE--#', str(kw_list.getyulesiscore())) \
        .replace('#--REG_YULESI_SCORE--#', str(reg_kw_list.getyulesiscore())) \
        .replace('<p>ANALYTICS LOG - last 100 lines:</p>', '<p>ANALYTICS LOG - last 100 lines:</p>' + html_str)


    f.close()

    logging.info("Score page response complete.")
    return returnhtml


def geterrorpage(errtext="Unknown Error"):
    """
    Populates error message with proper response and returns html

    :param str errtext: text of error
    :return: html page with error displayed
    :rtype: str

    """
    # Returns error page
    f = open("views/invalid_upload.html", "r")
    returnhtml = f.read().replace('##ERROR##', errtext)
    f.close()
    return returnhtml


def extractpdftext(file, testdownload_folder = None, RegDoc = False):
    """
    Extracts Text from PDF document referenced in given file argument

    :param fileStorage file: the PDF file to extract text from
    :param str testdownload_folder: specific download folder if necessary
    :param bool RegDoc: flag specifying whether this is a user doc or a regulatory doc
    :return: file's text
    :rtype: List[str]

    """
    localdownload_folder = ''

    file_text = []
    filename = file.filename
    chunk_size = int(applicationconfig.NUM_SEND_CHARS)
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
        logging.disable(logging.NOTSET)  # This re-enables logging
        logging.info("PDF file processed")

        file_text = longstringtostringlist(text, chunk_size)  # Converting long string to list of strings of size ____



    except FileNotFoundError as fnfe:
        logging.info(fnfe.strerror)
        # print(fnfe.strerror)
    if testdownload_folder is None and RegDoc is False:       # If this is not a test, remove file
        os.remove(localdownload_folder + filename)  # Removes created file from directory.
    return cleantext(file_text)


def extractmicrosoftdocxtext(file, testdownload_folder=None):
    """
    Extracts text from any ".docx" document and returns it.

    :param fileStorage file: the file to save
    :param str testdownload_folder: Specific download folder is necessary
    :return: file's text
    :rtype: List[str]

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

    file_text = splitintosize(file_text)
    return cleantext(file_text)


def splitintosize(file_text):
    """
    This function splits a list of keywords of any length into a lit of keywords eachof length specified by NUM_SEND_CHARS
    in 'applicationconfig.py'

    :param list file_text: list of document's words
    :return list file_text:

    """
    line = stringlisttolonglongstring(file_text)
    n = applicationconfig.NUM_SEND_CHARS

    file_text = [line[i:i + n] for i in range(0, len(line), n)]
    return file_text


def savefile(file, download_folder=None):
    """
    Save's given file to /Downloads folder"

    :param fileStorage file: the file to save
    :param str download_folder: specific download folder if necessary
    :return: void

    """

    # -- This is for testing, do not remove -- #
    if(download_folder is not None):
        DOWNLOAD_FOLDER = download_folder

    # filename = secure_filename(file.filename)
    filename = file.filename

    logging.info('saving file "' + filename + '"')
    file.save(os.path.join(DOWNLOAD_FOLDER, filename))  # saves uploaded files
    logging.info('"' + filename + '" saved')

    logging.info('opening file "' + filename + '"')  # Logging


def outputkeywordtotext(keylist, download_folder = 'Documents/Keywords.txt'):
    """
    This function will write Keywords from an analyzed document to a .txt file

    :param KeywordList keylist: list of document keywords
    :return: void

    """

    # TODO create file using document title of originating keywords

    try:
        logging.info("Outputting keywords to .txt...")
        file = open(download_folder, 'w')

        for i in range(0, keylist.uniquekeywords):
            word = keylist.list[i].word
            sal = keylist.list[i].salience
            freq = keylist.list[i].frequency
            keyscore = keylist.list[i].keywordscore

            file.write(word + "," + str(sal) + "," + str(freq) + "," + str(keyscore) + "\n")

        file.close()

        logging.info("Keyword .txt output complete.")

    except Exception as e:
        logging.info("Outputting keywords failed.")


def extractkeywordfromtxt(filename):
    """
    This function will extract keyword information from .txt file and place into KeywordList object

    :param str file: location of .txt file
    :return: keyword list in file
    :rtype: KeywordList

    """


    keyword_list = KeywordList()

    try:
        file = REGULATOR_FOLDER+filename
        i = 0
        f = open(file, 'r')
        logging.info("Extracting keyword info from " + filename)

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
        logging.info("keyword info extraction complete.")

    except Exception as e:
        logging.info("Keyword info extraction failed")


    return keyword_list


def cleantext(text_list):
    """
    Removes special characters from text

    :param List[str] text_list: a text string 
    :return: text_list with no special chars
    :rtype: List[str]

    """
    logging.info("Cleaning text of special characters...")
    printable = set(string.printable)

    for i in range(0, len(text_list)-1):
        text_list[i] = ''.join(filter(lambda x: x in string.printable, text_list[i]))

    logging.info("Clean text complete.")

    return text_list

def printStringList(textList):
    """
    Helper function that prints a list of strings

    :param List[str] textList: a text string
    :return: void
    """
    for i in range(0, len(textList)):
        print(textList[i])

def longstringtostringlist(longstring, strsize):
    """
    This functions splits a long string "longstring" into strings of size "strsize" and returns a list of those strings.

    :param string longstring: text of file
    :param int strsize: requested length of each string in created list of strings
    :return: file text
    :rtype: List[str]

    """

    return_list = [longstring[i:i + strsize] for i in range(0, len(longstring), strsize)]
    return return_list

def stringlisttolonglongstring(string_list):
    """
    Helper function to turn list of string into one long long string

    :param List[str] string_list: a string of text
    :return: file's text
    :rtype: long string
    """
    long_string = ""
    for i in range(0, len(string_list)):
        long_string += string_list[i].rstrip()
    return long_string


def createkeywordfromgoogleapientity(entity, file_text):
    """
    Creates a Keyword from a single entity that is returned by the google API

    :param Entity entity: Google API response entity object
    :param List[str] file_text: entire text of file
    :return: Populated Keyword object
    :rtype: Keyword
    """

    eName = entity['name']
    eType = entity['type']
    eSal = entity['salience']
    eFreq = getwordfrequency(eName, file_text)

    newKeyword = Keyword.Keyword(eName.upper(), eType, eSal, eFreq, 0)  # the value 0 refers to default keywordscore

    #for key, value in entity.metadata.items():
        #newKeyword.metadata[key] = value
    return newKeyword


def getwordfrequency(word, file_text):
    """
    Determines frequency of the given word in the file's text

    :param str word: Word to find frequency of
    :param List[str] filetext: list of string containing entire text of file
    :return: frequency of word parameter in text
    :rtype: int
    """
    # TODO: Only populate longlongfiletext once, it is very inefficient the way it is now.
    longlongfiletext = common_functions.stringlisttolonglongstring(file_text).replace('\n', '')
    test = longlongfiletext.count(word)
    return longlongfiletext.count(word)


def getregulatorydoctext(filename):
    """
    Looks in the RegulatoryDocuments folder for the file with the given file name and return's its text as a list of string

    :param str filename: name of regulatory file without file ending on it
    :return: list of strings of length 1024 containing text of file
    :rtype: List[str]

    """
    try:
        logging.info('opening regulatory document')

        with open(REGULATOR_FOLDER + filename, 'rb') as fp:
            file = FileStorage(fp)

        reg_text = extractpdftext(file, RegDoc=True)
    except FileNotFoundError and ValueError as e:
        logging.error('could not access regulatory document"' + filename + '"')

    # print(reg_text)
    return reg_text


def kwhighestfrequencies(keyword_list, numtopkws = 10):
    """
    Returns the top 10 most frequent Keywords in the user's uploaded file

    :param KeywordList keyword_list: List of Keyword objects
    :return: Keywords with highest frequencies
    :rtype: List[Keyword]

    """

    kwlist = list(keyword_list.list)
    topkeywords = []
    topKeywordfreqs = []

    # This loop finds the 10 most common keywords in the keyword_list
    i = 0
    while i < numtopkws and len(kwlist) > 0:
        topkeywordfreq = max(x.frequency for x in kwlist)
        topKeywordfreqs.append(topkeywordfreq)

        topkeyword = next(kw for kw in kwlist if kw.frequency == topkeywordfreq)
        topkeywords.append(topkeyword)

        kwlist[:] = [x for x in kwlist if x.word != topkeyword.word] # removes the previously added item so it does not get chosen again
        i += 1

    return topkeywords

def kwhighestkeyscores(keyword_list):
    """
    Returns ten Keywords with the highest Keyword scores

    :param KeywordList keyword_list: list of Keyword objects
    :return: list of top keyword scores
    :rtype: List[Keyword]

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


def plotkeywordsalience(keyword_list1, keyword_list2, doc1name='doc1', doc2name = 'doc2'):
    """
    Plots salience of most frequently used keywords. Pulls KWs from list1, compares against list2

    :param KeywordList keyword_list1: user KeywordList
    :param KeywordList keyword_list2: regulatory KeywordList
    :param str doc1name: user document name
    :param str doc2name: regulatory document name
    :return: void

    """

    # Clearing previous graph just to be safe
    pyplot.clf()

    kwlist1 = common_functions.kwhighestfrequencies(keyword_list1)
    kwlist2 = common_functions.kwhighestfrequencies(keyword_list2)

    logging.info("Plotting keyword salience...")

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
        pyplot.savefig(DOWNLOAD_FOLDER + 'topsalience.png')
        return
    x = np.arange(len(my_xticks))
    pyplot.bar(x, y, width=w, align='center', color='blue', label='User doc: "' + doc1name + '"')
    pyplot.bar(x+w, p, width=w, align='center', color='r', label='Regulatory doc: "' + doc2name + '"')
    pyplot.xticks(x + w/2, my_xticks, fontsize=8, color='black', rotation=90)
    pyplot.yticks(fontsize=8)
    pyplot.title('Salience of Most Common Keywords In File', fontweight='bold')
    pyplot.xlabel('Keywords (in order of frequency in uploaded document)', fontsize=10, color='red')
    pyplot.ylabel('Salience', fontsize=10, color='red')
    pyplot.legend()
    pyplot.tight_layout()
    pyplot.savefig(DOWNLOAD_FOLDER + 'topsalience.png')

    logging.info("Plot complete.")
    # pyplot.show()


def plotkeywordscores(keyword_list1, keyword_list2, doc1name='doc1', doc2name = 'doc2'):
    """
    Plots keyword score of most frequently used keywords. Pulls KWs from list1, compares against list2

    :param KeywordList keyword_list1: user KeywordList
    :param KeywordList keyword_list2: regulatory KeywordList
    :param str doc1name: user document name
    :param str doc2name: regulatory document name
    :return: void

    """

    # Clearing previous graph just to be safe
    pyplot.clf()

    kwlist1 = common_functions.kwhighestkeyscores(keyword_list1)
    kwlist2 = common_functions.kwhighestkeyscores(keyword_list2)

    logging.info("Plotting keyword scores...")

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
    pyplot.bar(x, y, width=w, align='center', color='blue', label='User doc: "' + doc1name + '"')
    pyplot.bar(x+w, p, width=w, align='center', color='r', label='Regulatory doc: "' + doc2name + '"')
    pyplot.xticks(x + w/2, my_xticks, fontsize=8, color='black', rotation=90)
    pyplot.yticks(fontsize=8)
    pyplot.title('Keyword Score of Most Common Keywords In File', fontweight='bold')
    pyplot.xlabel('Keywords (in order of keyword score in uploaded document)', fontsize=10, color='red')
    pyplot.ylabel('Keyword Score', fontsize=10, color='red')
    pyplot.legend()
    pyplot.tight_layout()
    pyplot.savefig(DOWNLOAD_FOLDER + 'topkeywordscores.png')

    logging.info("Plotting complete.")
    # pyplot.show()

def plotkeywordfrequency(keyword_list1, keyword_list2, doc1name='doc1', doc2name = 'doc2'):
    """
    Plots keyword score of most frequently used keywords. Saves graph to "/Downloads" folder

    :param KeywordList keyword_list1: user document keywords
    :param KeywordList keyword_list2: regulatory document keywords
    :param str doc1name: name of user document
    :param str doc2name: name of regulatory document
    :return: void
    
    """

    # Clearing previous graph just to be safe
    pyplot.clf()

    kwlist1 = common_functions.kwhighestfrequencies(keyword_list1)
    kwlist2 = common_functions.kwhighestfrequencies(keyword_list2)

    logging.info("Plotting keyword frequency...")

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
                y.append(kwlist1[x].frequency)
                p.append(kwlist2[s].frequency)
                d += 1
                break
            else:
                s += 1

    if d == 0:
        pyplot.bar(x, y)
        pyplot.clf()
        pyplot.title('NO COMMON KEYWORDS TO PLOT', fontweight='bold')
        pyplot.savefig(DOWNLOAD_FOLDER + 'topkeywordfrequency.png')
        return
    x = np.arange(len(my_xticks))
    pyplot.bar(x, y, width=w, align='center', color='blue', label='User doc: "' + doc1name + '"')
    pyplot.bar(x+w, p, width=w, align='center', color='r', label='Regulatory doc: "' + doc2name + '"')
    pyplot.xticks(x + w/2, my_xticks, fontsize=8, color='black', rotation=90)
    pyplot.yticks(fontsize=8)
    pyplot.title('Keyword Frequencies of Most Common Keywords In File', fontweight='bold')
    pyplot.xlabel('Keywords (in order of keyword score in uploaded document)', fontsize=10, color='red')
    pyplot.ylabel('Frequency', fontsize=10, color='red')
    pyplot.legend()
    pyplot.tight_layout()
    pyplot.savefig(DOWNLOAD_FOLDER + 'topkeywordfrequency.png')

    logging.info("Plotting complete.")
    # pyplot.show()


def printanalytics(filename, regfilename, keywordlist, regkeywordlist, calctime):
    """
        prints the data passed in te argument to the ever-increasing file that contains data analytics information

        :param str printstr: string to output to file
        :return: void

        """

    str_list = []

    # KEEP THIS FORMATTING
    str_list.append(str(datetime.datetime.now()) + ' ; ' + '[' + str(round(calctime, 3)) + ' sec.] ; ' + filename + ' ; ' + str(len(keywordlist.list))\
                    + ' ; ' + regfilename + ' ; ' + str(len(regkeywordlist.list)) + ' ; \n')

    printstr = str_list[0]

    f = open(DOCUMENTS_FOLDER + 'Analytics.txt', 'r+')
    text = f.read()
    f.close()

    f = open(DOCUMENTS_FOLDER + 'Analytics.txt', 'w')
    f.write(printstr + text)
    f.close()



