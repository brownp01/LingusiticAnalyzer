import os
import PyPDF2
import requests
from flask import Flask
from flask import Response, request
from werkzeug.utils import secure_filename
import logging
from functionsv1 import common_functions
from functionsv1 import analyze_functions
# import textract


def homeCount():
    returnVal = homeCount.counter
    homeCount.counter += 1
    return returnVal


homeCount.counter = 0


def extractpdftext(file, uploadfolder):
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

    filename = secure_filename(file.filename)

    common_functions.log('saving file "' + filename + '"')
    file.save(os.path.join(uploadfolder, filename))  # saves uploaded files
    common_functions.log('"' + filename + '" saved')

    logging.info('opening file "' + filename + '"')  # Logging

    # TODO: Find other library to read PDFs with. PyPDF2 does not work for all files.
    pdfFileObj = open(uploadfolder + filename, 'rb')  # Opens uploaded file
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    for i in range(0, pdfReader.numPages):
        pageObject = pdfReader.getPage(i)

        # saves text of uploaded pdf into a list of strings
        temp = pageObject.extractText()
        file_text.append(pageObject.extractText().strip('\n'))
        # print(file_text[len(file_text) - 1])

    os.remove(uploadfolder + filename)  # Removes created file from directory.
    return file_text


def extractmicrosoftdoctext(file, uploadfolder):
    """
    @summary:
    @param file:
    @type file:
    @param uploadfolder:
    @type uploadfolder:
    @return:
    @rtype:
    """
    return []


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

