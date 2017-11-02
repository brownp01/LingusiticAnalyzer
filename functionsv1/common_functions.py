import os
from werkzeug.utils import secure_filename
import logging
from functionsv1 import common_functions
import docx
import string
import io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import Keyword
import KeywordList


UPLOAD_FOLDER = 'downloads/'

def homeCount():
    returnVal = homeCount.counter
    homeCount.counter += 1
    return returnVal


homeCount.counter = 0


def extractpdftext(file):
    """
    @summary:   extracts Text from PDF document referenced in given file argument
    @param file:    the object containing the file's information
    @type file:     fileStorage
    @return: list containing the text of the PDF
    @rtype: string
    """
    file_text = []
    filename = file.filename

    try:
        savefile(file)

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

        infile = open(UPLOAD_FOLDER + file.filename, 'rb')
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page)
        infile.close()
        converter.close()
        text = output.getvalue()        # Worry - An incredibly long string may crash our application
        output.close
        # --------End of PDFMiner reading --------#
        logging.disable(logging.NOTSET) # This re-enables logging
        log("PDF file processed")

        file_text = longstringtostringlist(text, 1024)  # Converting long string to list of strings of size 1024

        # ----------This is the PyPDF2 PDF Reader (Deprecated - does not work with all PDFs) ----------#
        """
        pdfFileObj = open(UPLOAD_FOLDER + filename, 'rb')  # Opens uploaded file
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        for i in range(0, pdfReader.numPages):
            pageObject = pdfReader.getPage(i)

            # saves text of uploaded pdf into a list of strings
            temp = pageObject.extractText()
            file_text.append(pageObject.extractText().strip('\n'))
            # print(file_text[len(file_text) - 1])
        """

    except RuntimeError:
        file_text.append("**ERROR - unable to process file: " + RuntimeError + "**")
        log("**ERROR - unable to process file: " + RuntimeError + "**")
    os.remove(UPLOAD_FOLDER + filename)  # Removes created file from directory.
    return cleantext(file_text)





def extractmicrosoftdocxtext(file):
    """
    @summary:
    @param file:
    @type file:
    @param uploadfolder:
    @type uploadfolder:
    @return:
    @rtype:
    """
    file_text = []
    savefile(file)

    doc = docx.Document(UPLOAD_FOLDER + file.filename)

    for para in doc.paragraphs:
        if len(para.text) != 0:
            file_text.append(para.text.strip('\t'))

    os.remove(UPLOAD_FOLDER + file.filename)  # Removes created file from directory.
    return cleantext(file_text)


def log(text):
    """
    @summary: This function looks at string to be logged and decides the best way to log it. This function exists in
    case we need to add more complex logging functionality and don't want to handle logging complexities inline, as
    this would be ugly.
    @param text: message to be logged
    @type text: string
    @return: void
    @rtype: void
    """
    if "WARN" in text:
        logging.warning(text)
    else:
        logging.info(text)


def savefile(file):
    filename = secure_filename(file.filename)

    common_functions.log('saving file "' + filename + '"')
    file.save(os.path.join(UPLOAD_FOLDER, filename))  # saves uploaded files
    common_functions.log('"' + filename + '" saved')

    logging.info('opening file "' + filename + '"')  # Logging


def outputkeywordtotext(keylist):
    """
    @summary: This function will write keywords from an analyzed document to a .txt file
    @param keylist: KeywordList object containing keywords from analyzed document
    @type object: KeywordList
    @return: void
    """
    #TODO create file using document title of originating keywords
    file = open('Documents/test.txt', 'w')

    #TODO determine best format and information needed to save from Keyword object for future use
    for i in range(0, keylist.uniquekeywords):
        file.write(keylist.list[i].word + "," + str(keylist.list[i].frequency) + "\n")

    file.close()

def extractkeywordfromtxt(file):
    """
    @summary: This function will extract keyword information from .txt file and place into KeywordList object
    @param file: location of .txt file
    @type file: .txt
    @return: void
    """
    keyword_list = KeywordList.KeywordList
    i = 0

    f = open(file, 'r')
    for line in f:
        line_list = line.split(',')
        #TODO modify input to Keyword Object to fit overall needs
        newKeyword = Keyword.Keyword(line_list[i], int(line_list[i+1].rstrip('\n')))
        keyword_list.insertkeyword(newKeyword)

    f.close()


def cleantext(textlist):
    """
    @summary:
    @param textlist: a list of strings to remove strange characters from
    @type textlist:
    @return:
    @rtype:
    """
    printable = set(string.printable)

    for i in range(0, len(textlist)-1):
        textlist[i] = ''.join(filter(lambda x: x in string.printable, textlist[i]))

    return textlist

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
        long_string += string_list[i]

def createkeywordfromgoogleapientity(entity):
    """
    @summary: Creates a keyword from a single entity that is returned by the google API
    @param entity: google API response entity
    @type entity: google API response entity
    @return: populated instance of Keyword class
    @rtype: Keyword
    """
    newKeyword = Keyword.Keyword(entity.name, entity.type)
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





