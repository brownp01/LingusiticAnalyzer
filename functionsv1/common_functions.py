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
#import applicationconfig
import json
import operator


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
    Summary: Function that handles uploaded user document. The following occurs:

    1. Extracts text from a pdf file with :func:`extractpdftext`.
    2. Identifies keywords with :func:`analyze_functions.identifykeywords`.
    3. Calculates various scores for each keyword with :func:`analyze_functions.calculatescores` and
       :func:`KeywordList.KeywordList.calculateavgscores`.
    4. Exports keyword information to a *.txt* file via :func:`outputkeywordtotext`.
    5. Determines total word count for a *file*. The value is stored in the variable *wordcount*


    :param fileStorage file: file to be interpreted
    :param str localuploadfolder: Place to temporary store file so it can be read from
    :return: list of file's Keywords, wordcount
    :rtype: KeywordList, int

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


    wordcount = 0

    for chunk in file_text:
        wordcount = wordcount + len(chunk.split())

    return [keyword_list, wordcount]


def interpretexistingfile(regfilename):
    """
    Summary: Function that handles a newly uploaded regulatory doc or an existing regulatory document. The following occurs:

    1. Checks *regfilename* to determine if it's a .pdf. If it's a .pdf, then that means that this is the first time
       a regulatory document has been published to the app. Analysis of the document needs to occur.

       - Extracts text from a pdf file with :func:`getregulatorydoctext`.
       - Identifies keywords with :func:`analyze_functions.identifykeywords`.
       - Calculates various scores for each keyword with :func:`analyze_functions.calculatescores` and
         :func:`KeywordList.KeywordList.calculateavgscores`.
       - The file extension is changed from *.pdf* to *.txt*. This is done so that the existing filename with extension can
         be used when exporting information to *.txt* file.
       - Exports keyword information to a *.txt* file via :func:`outputkeywordtotext`.
       - 'views/index.html' is edited to include the new regulatory document file path for future selection on the app
         home page. The file path points to the *.txt* version of the document so analysis does not occur again.

    2. If the *regfilename* is not a *pdf* file, then it's a *txt* file. Analysis of the file does not need to occur
       since it was previously done.

       - The keywords with associated information are extracted from the *txt* file via :func:`extractkeywordfromtxt`.


    :param str regfilename: name of regulatory file
    :return: Keyword list of regulatory document.
    :rtype: KeywordList

    """
    if regfilename[-3:] == 'pdf':
        reg_text = common_functions.getregulatorydoctext(regfilename)
        reg_keyword_list = analyze_functions.identifykeywords(reg_text)
        analyze_functions.calculatescores(reg_keyword_list, reg_text)
        reg_keyword_list.calculateavgscores()
        regfilenameTXT = common_functions.changefileextension(regfilename)
        common_functions.outputkeywordtotext(reg_keyword_list, REGULATOR_FOLDER + regfilenameTXT)

        #------- Change filename extension for reg doc path in 'index.html' to .txt after initial PDF analysis -------#

        fhtml = open('views/index.html')
        text = fhtml.read()
        newhtml = text.replace('<option value=' + '"' + regfilename + '"' + '>',
                               '<option value=' + '"' + regfilenameTXT + '"' + '>')
        fhtml.close()
        newindexhtml = open('views/index.html', 'w')
        newindexhtml.write(newhtml)
        newindexhtml.close()

    else:
        reg_keyword_list = common_functions.extractkeywordfromtxt(regfilename)

    common_functions.outputkeywordtotext(reg_keyword_list, 'Documents/Reg_Keywords.txt')

    return reg_keyword_list


def changefileextension(regfilename):
    """
    Summary: Changes the file name string from *.pdf* to *.txt*.


    :param str regfilename: name of regulatory file
    :return: string with *.txt* file extension
    :rtype: str

    """

    temp = list(regfilename)
    size = len(regfilename)
    temp[size-3] = "t"
    temp[size-2] = "x"
    temp[size-1] = "t"
    regfilenameTXT = "".join(temp)

    return regfilenameTXT


def getscorepage(kw_list, reg_kw_list, userdocwordcount, filename, regfilename):
    """
    Summary: Returns 'views/score_response.html' page that is populated with proper calculated Keyword, Comparison,
    and Yule's scores.


    :param KeywordList kw_list: list of user document's Keyword objects
    :param KeywordList reg_kw_list: list of regulatory document's Keywords
    :param int userdocwordcount: word count of user document
    :param str filename: user document's file name
    :param str regfilename: regulatory document's file name
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


    numofkwoccurences = 0

    for kw in kw_list.list:
        numofkwoccurences += kw.frequency



    f = open("views/score_response.html", "r")
    returnhtml = f.read().replace('#--KEYWORD_SCORE--#', str(kw_list.getavgkeywordscore())). \
        replace('#--YULESK_SCORE--#', str(kw_list.getyuleskscore()))\
        .replace('#--DOCUMENT_SCORE--#', str(kw_list.getdocumentscore()))\
        .replace('#--COMPARISON_SCORE--#', str(analyze_functions.calculatecomparisonscore(kw_list, reg_kw_list))) \
        .replace('#-USER-DOC-NAME-#', filename[:-4]) \
        .replace('#-REG-DOC-NAME-#', regfilename[:-4]) \
        .replace('#--REG_YULESK_SCORE--#', str(reg_kw_list.getyuleskscore())) \
        .replace('#--YULESI_SCORE--#', str(kw_list.getyulesiscore())) \
        .replace('#--REG_YULESI_SCORE--#', str(reg_kw_list.getyulesiscore())) \
        .replace('<p>ANALYTICS LOG - last 100 lines:</p>', '<p>ANALYTICS LOG - last 100 lines:</p>' + html_str) \
        .replace('#--USER-DOC-KEYWORD-NUM--#', str(len(kw_list.list))) \
        .replace('#--REG-DOC-KEYWORD-NUM--#', str(len(reg_kw_list.list))) \
        .replace('#--KEYWORDS-COMPRISE--#', str('%.3f' % ((numofkwoccurences/userdocwordcount) * 100)) + '%')

    f.close()

    logging.info("Score page response complete.")
    return returnhtml


def geterrorpage(errtext="Unknown Error"):
    """
    Summary: Populates error message with proper response and returns html


    :param str errtext: text of error
    :return: html page with error displayed
    :rtype: str

    """

    common_functions.writeToConfig('NEW_DOC_FLAG', 'false')

    # Returns error page
    f = open("views/invalid_upload.html", "r")
    returnhtml = f.read().replace('##ERROR##', errtext)
    f.close()
    return returnhtml


def extractpdftext(file, testdownload_folder = None, RegDoc = False):
    """
    Summary: Extracts text from PDF document referenced in the given file argument using the :mod:`PDFMiner` python package.

    The first part of the code assigns a "chunk" size via the value *NUM_SEND_CHARS* set in /applicationconfig.json.
    *chunk_size* is designated to break up a long string of text into a list of strings, if needed. The default setting
    for this allows for a single string of text.

    Before starting the PDF text extraction, logging is disabled due to the amount of statements PDFMiner produces in the
    log.


    :param fileStorage file: the PDF file to extract text from
    :param str testdownload_folder: specific download folder if necessary
    :param bool RegDoc: flag specifying whether this is a user doc or a regulatory doc
    :return: file's text
    :rtype: List[str]
    :raises: FileNotFoundError

    """
    localdownload_folder = ''

    file_text = []
    filename = file.filename

    data = json.load((open('applicationconfig.json')))

    chunk_size = int(data['NUM_SEND_CHARS'])
    try:
        # -- This is for testing, do not remove -- #
        if testdownload_folder is None and RegDoc is False:
            localdownload_folder = DOWNLOAD_FOLDER
            savefile(file, localdownload_folder)
        elif testdownload_folder is not None:
            localdownload_folder = testdownload_folder

        # PdfMiner writes an insane amount of logging statements (one per parsed word, it seems).
        # Remove the below line if you would like to see them.
        logging.disable(logging.INFO)
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

        file_text = longstringtostringlist(text, chunk_size)  # Converting long string to list of strings of size


    except FileNotFoundError as fnfe:
        logging.info(fnfe.strerror)
        # print(fnfe.strerror)
    if testdownload_folder is None and RegDoc is False:       # If this is not a test, remove file
        os.remove(localdownload_folder + filename)  # Removes created file from directory.
    return cleantext(file_text)


def extractmicrosoftdocxtext(file, testdownload_folder=None):
    """
    Summary: Extracts text from any *.docx* document and returns it.


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
    Summary: This function splits a list of keywords of any length into a list of keywords each of length specified by
    NUM_SEND_CHARS in '/applicationconfig.json'


    :param list file_text: list of document's words
    :return: file_text
    :rtype: List[str]

    """
    line = stringlisttolonglongstring(file_text)

    data = json.load((open('applicationconfig.json')))
    n = int(data['NUM_SEND_CHARS'])
    file_text = [line[i:i + n] for i in range(0, len(line), n)]

    return file_text


def savefile(file, download_folder=None):
    """
    Summary: Save's given file to '/Downloads' folder.


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
    Summary: This function will write Keywords and associated data from an analyzed document to a *.txt* file.

    - The first line written to the file is the Yule's K, Yule's I and average keyscore of a :class:`KeywordList` object.
    - The second and following lines include the Keyword, Salience score, Frequency of keyword, and the Keyword score from
      the :class:`Keyword` object.
    - An **Exception** will raise if the output of Keywords to a *.txt* file does not fully complete. This is an issue that
      occurs in the AWS Beanstalk environment. Running the app on a local machine should not throw the Exception, based
      on testing.


    :param KeywordList keylist: list of document keywords
    :param str download_folder: location to save the *.txt* file.
    :return: void
    :raises: Exception

    """

    counter = 0
    try:
        logging.info("Outputting keywords to .txt...")

        file = open(download_folder, 'w')
        yulesK = keylist.yuleskscore
        yulesI = keylist.yulesiscore
        avgkeyscore = keylist.avgkeywordscore

        file.write(str(yulesK) + "," + str(yulesI) + "," + str(avgkeyscore) + "\n")

        # ------alphabetical order------- #
        # TODO: Put in frequency order
        sortedkeywords = sorted(keylist.list, key=operator.attrgetter('frequency'))

        for i in range(0, keylist.uniquekeywords):
            word = keylist.list[i].word
            sal = keylist.list[i].salience
            freq = keylist.list[i].frequency
            keyscore = keylist.list[i].keywordscore

            file.write(word + "," + str(sal) + "," + str(freq) + "," + str(keyscore) + "\n")
            counter += 1

        file.close()

        logging.info("Keyword .txt output complete.")

    except Exception as e:
        logging.info("*** Output keywords failed: " + str(counter) + "/" + str(len(keylist.list)) + " keywords outputted ***")


def extractkeywordfromtxt(filename):
    """
    Summary: This function will extract existing keyword information from *.txt file* and place it into the :class:`KeywordList`
    object.

    - This function will read in the first line of an existing *.txt* file and place the Yule's K, Yule's I, and average
      keyword score into a :class:`KeywordList` object.
    - For the second and remaining lines, the Keyword, Salience score, Frequency of keyword, and Keyword score are placed
      into a :class:`Keyword` object, and then inserted in a :class:`KeywordList` object via the
      :func:`KeywordList.KeywordList.insertkeyword` function.
    - An **Exception** will raise if the extraction of keywords from a *.txt* file does not fully complete. This is an
      issue that occurs in the AWS Beanstalk environment. Running the app on a local machine should not throw the Exception,
      based on testing.


    :param str file: location of .txt file
    :return: keyword list in file
    :rtype: KeywordList
    :raises: Exception

    """

    keyword_list = KeywordList()

    try:
        file = REGULATOR_FOLDER+filename
        i = 0
        f = open(file, 'r', errors='replace')

        logging.info("Extracting keyword info from " + filename)

        line_list = f.readline().split(',')
        yulesk = line_list[i]
        yulesi = line_list[i+1]
        avgscore = line_list[i+2]
        keyword_list.yuleskscore = float(float(yulesk))
        keyword_list.yulesiscore = float(float(yulesi))
        keyword_list.avgkeywordscore = float(float(avgscore.rstrip('\n')))

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
        logging.info("*** Keyword info extraction failed(" + str(keyword_list.uniquekeywords) + " uploaded). ***")

    return keyword_list


def cleantext(text_list):
    """
    Summary: Removes special characters from text.

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
    Summary: Helper function that prints a list of strings


    :param List[str] textList: a text string
    :return: void
    """
    for i in range(0, len(textList)):
        print(textList[i])

def longstringtostringlist(longstring, strsize):
    """
    Summary: This functions splits a long string *longstring* into strings of size *strsize* and returns a list of those
    strings.


    :param str longstring: text of file
    :param int strsize: requested length of each string in created list of strings
    :return: return_list
    :rtype: List[str]

    """

    return_list = [longstring[i:i + strsize] for i in range(0, len(longstring), strsize)]

    return return_list

def stringlisttolonglongstring(string_list):
    """
    Summary: Helper function to turn a list of strings into one long long string.

    :param List[str] string_list: a string of text
    :return: file's text
    :rtype: long str

    """

    long_string = ""
    for i in range(0, len(string_list)):
        long_string += string_list[i].rstrip()

    return long_string


def createkeywordfromgoogleapientity(entity, file_text):
    """
    Summary: Creates a Keyword from a single entity that is returned by the google NLP API.

    - The 'name' or Keyword, Type of keyword, Salience score, and Frequency of the keyword is inputted in the
      :class:`Keyword` object. A default value of *0* is used for the keyword score. Keyword score is determined further
      on in the app.
    - The frequency of a keyword is found by using the :func:`getwordfrequency` function.


    :param dict entity: Google API response entity object
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
    Summary: Determines frequency of the given word in the file's text


    :param str word: Word to find frequency of
    :param List[str] file_text: list of string containing entire text of file
    :return: frequency of word parameter in text
    :rtype: int
    """
    # TODO: Only populate longlongfiletext once, it is very inefficient the way it is now.
    longlongfiletext = common_functions.stringlisttolonglongstring(file_text).replace('\n', '')
    test = longlongfiletext.count(word)
    return longlongfiletext.count(word)


def getregulatorydoctext(filename):
    """
    Summary: Looks in the '/RegulatoryDocuments' folder for the file with the given *filename* and return's its text as a
    list of strings. The :func:`extractpdftext` function is utilized.


    :param str filename: name of regulatory file without file ending on it
    :return: file text
    :rtype: List[str]
    :raises: FileNotFoundError

    """
    try:
        logging.info('opening regulatory document')

        with open(REGULATOR_FOLDER + filename, 'rb') as fp:
            file = FileStorage(fp)

        reg_text = extractpdftext(file, RegDoc=True)

    except FileNotFoundError and ValueError as e:
        logging.error('could not access regulatory document"' + filename + '"')

    return reg_text


def kwhighestfrequencies(keyword_list, numtopkws = 10):
    """
    Summary: Returns the top 10 most frequent Keywords in an uploaded file.


    :param KeywordList keyword_list: List of Keyword objects
    :param int numtopkws: number of keywords to return.
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
    Summary: Returns ten Keywords with the highest Keyword scores


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
    Summary: Plots salience scores of most frequently used keywords. Pulls keywords from *keyword_list1* and compares
    against *keyword_list2*. The :mod:`matplotlib` python package is used to aide in plotting the data.

    If there are no common keywords to plot, a blank plot will display with the title "No Common Keywords to Plot".

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
        logging.info("No common keywords to plot")
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
    Summary: Plots keyword score of the most frequently used keywords. Pulls keywords from *keyword_list1* and compares
    against *keyword_list2*. The :mod:`matplotlib` python package is used to aide in plotting the data.

    If there are no common keywords to plot, a blank plot will display with the title "No Common Keywords to Plot".


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
        logging.info("No keyword scores to plot")
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
    Summary: Plots keyword score of most frequently used keywords. Pulls keywords from *keyword_list1* and compares
    against *keyword_list2*. The :mod:`matplotlib` python package is used to aide in plotting the data.

    If there are no common keywords to plot, a blank plot will display with the title "No Common Keywords to Plot".


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
        logging.info("No keyword frequency to plot")
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
    Summary: Saves the data passed in the argument to the ever-increasing file '/downloads/Analytics.txt' that contains
    data analytics information.
    Analytic information includes:

    - Date/Time
    - Processing time
    - user doc file name and number of keywords
    - regulatory doc file name and number of keywords


    :param str filename: name of user document file
    :param str regfilename: name of regulatory document file
    :param KeywordList keywordlist: user document Keyword list
    :param KeywordList regkeywordlist: regulatory document Keyword list.
    :param int calctime: processing time of app.
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


def generatebubblecsv(kw_list, reg_kw_list):
    """
    Summary: Creates a new *csv* file with all the keywords. The *csv* file is used to generate the Bubble Chart.


    :param KeywordList kw_list: list of doc keywords
    :param KeywordList reg_kw_list: list of reg doc keywords
    :return: void
    :raises: Exception

    """

    try:
        logging.info("Generating Bubble Chart CSV...")

        f = open(DOCUMENTS_FOLDER + 'csvkeywords.csv', 'w')
        f.writelines(["keyword,frequency,salience\n", '----------------\n'])

        breakCount = -1

        for i in range(0, len(kw_list.list)):
            # in order to preserve color scheme, keywords from different files must alternate, so if one runs out, we stop.

            data = json.load(open('applicationconfig.json'))
            if i >= len(reg_kw_list.list) or i >= int(data['MAX_BUBBLES']):
                breakCount = i
                writeToConfig("ACTUAL_BUBBLES", i)
                break
            f.write(kw_list.list[i].word + ',' + str(kw_list.list[i].frequency) + ',' + str(kw_list.list[i].salience) + '\n')
            f.write(reg_kw_list.list[i].word + ',' + str(reg_kw_list.list[i].frequency) + ',' + str(reg_kw_list.list[i].salience) + '\n')

        if breakCount != -1:
            writeToConfig("ACTUAL_BUBBLES", breakCount)
        else:
            writeToConfig("ACTUAL_BUBBLES", len(kw_list.list))

        f.close()

        logging.info("Bubble Chart CSV generation successful")

    except Exception as e:
        logging.info("Bubble Chart CSV generation failed.")


def writeToConfig(key, value):
    """
    Summary: Writes *value* into the '/applicationconfig.json' file.


    :param str key: variable in which *value* is being written to
    :param value: value
    :return: none

    """

    data = json.load((open('applicationconfig.json')))
    data[key] = value
    with open('applicationconfig.json', 'w') as outfile:
        json.dump(data, outfile)