import os
import PyPDF2
import requests
from flask import Flask
from flask import Response, request
from werkzeug.utils import secure_filename
import logging
from functionsv1 import common_functions
import docx
import string
from functionsv1 import analyze_functions
from pdfrw import PdfReader
# import textract

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
    @param uploadfolder:   parameter containing the location where the file is to be temporarily saved
    @type uploadfolder: string
    @return: list containing the text of the PDF
    @rtype: string
    """
    file_text = []
    savefile(file)

    filename = file.filename

    # TODO: Find other library to read PDFs with. PyPDF2 does not work for all files.
    pdfFileObj = open(UPLOAD_FOLDER + filename, 'rb')  # Opens uploaded file
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    for i in range(0, pdfReader.numPages):
        pageObject = pdfReader.getPage(i)

        # saves text of uploaded pdf into a list of strings
        temp = pageObject.extractText()
        file_text.append(pageObject.extractText().strip('\n'))
        # print(file_text[len(file_text) - 1])

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

    @param textList:
    @type textList:
    @return:
    @rtype:
    """
    for i in range(0, len(textList)-1):
        print(textList[i])