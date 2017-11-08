from unittest import TestCase
from unittest import TestCase
from functionsv1 import common_functions
from werkzeug import datastructures
from functionsv1 import common_functions
import logging
import os

DOWNLOADS_FOLDER = '/Users/tlblanton/Documents/UC_Denver/2017_fall/senior_design/linguistic_analyzer/11_7_17\
/LinguisticAnalyzer/unit_tests/test_pdfs/'


class TestExtractpdftext(TestCase):
    def test_extractpdftext(self):
        file = ''
        testFileName = 'test_extractpdftext.pdf'
        try:
            #opening test file
            file = datastructures.FileStorage(filename=testFileName,
                                              content_type="application/pdf", name='datafile')
            if file.filename is None:
                self.fail("File could not be opened")

            # Creating blank file in downloads folder
            # open(DOWNLOADS_FOLDER + file.filename, 'a').close()

            #calling to test functions
            file_text = common_functions.extractpdftext(file, DOWNLOADS_FOLDER)

            longlongfiletext = common_functions.stringlisttolonglongstring(file_text)


            self.assertTrue(len(file_text) is not 0)
            self.assertEqual(longlongfiletext, 'this this is is a a test test with with two two of of each each of of these these words words')
            self.assertTrue(longlongfiletext.count('test') is 2)
            logging.info('TestExtractpdftext PASSED')
        except Exception as e:
            logging.info("Test Failed")
            self.fail('Unable to convert PDF to text')
        finally:
            file.close()