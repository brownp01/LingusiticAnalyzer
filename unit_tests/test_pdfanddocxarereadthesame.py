from unittest import TestCase
from functionsv1 import common_functions
from werkzeug import datastructures
import logging


# TODO: Fix downloads folder issue
DOCX_DOWNLOADS_FOLDER = 'unit_tests/test_docxs/'

# TODO: Fix downloads folder issue
PDF_DOWNLOADS_FOLDER = 'unit_tests/test_pdfs/'

class TestEnsurepdfanddocxarereadthesame(TestCase):
    def test_ensurepdfanddocarereadthesame(self):
        """
        Summary: tests whether extractpdftext() and extractdocxtext() return 
        the same exact information when given the same document in different formats
        
        """
        # #----------------READING DOCX----------------# #
        docxfile = ''
        pdffile = ''
        docxtestfilename = 'test_extractdocxtext.docx'
        pdftesttilename = 'test_extractpdftext.pdf'
        longlongpdffiletext = ''
        longlongdocxfiletext = ''

        try:
            try:
                # opening test file
                docxfile = datastructures.FileStorage(filename=docxtestfilename,
                                                  content_type="application/pdf", name='datafile')
                if docxfile.filename is None:
                    self.fail("File could not be opened")

                # Creating blank file in downloads folder
                # open(DOWNLOADS_FOLDER + file.filename, 'a').close()

                # calling to test functions
                docxfile_text = common_functions.extractmicrosoftdocxtext(docxfile, DOCX_DOWNLOADS_FOLDER)

                longlongdocxfiletext = common_functions.stringlisttolonglongstring(docxfile_text)

            except FileNotFoundError as fnfe:
                logging.info("Unable to convert Docx to text")
                self.fail('Unable to convert Docx to text')
            finally:
                docxfile.close()

            try:
                # opening test file
                pdffile = datastructures.FileStorage(filename=pdftesttilename,
                                                  content_type="application/pdf", name='datafile')
                if pdffile.filename is None:
                    self.fail("File could not be opened")

                # Creating blank file in downloads folder
                # open(DOWNLOADS_FOLDER + file.filename, 'a').close()

                # calling to test functions
                pdffile_text = common_functions.extractpdftext(pdffile, PDF_DOWNLOADS_FOLDER)

                longlongpdffiletext = common_functions.stringlisttolonglongstring(pdffile_text)
            except Exception as e:
                logging.info("Test Failed")
                self.fail('Unable to convert PDF to text')
            finally:
                pdffile.close()
            self.assertTrue(len(longlongpdffiletext) != 0)
            self.assertTrue(len(longlongdocxfiletext) != 0)
            self.assertEqual(longlongdocxfiletext, longlongpdffiletext)

        except Exception as e:
            logging.info("Unknown exception. Test failed.")
            self.fail("Unknown exception. Test failed.")
