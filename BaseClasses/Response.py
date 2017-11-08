class Response:
    """
    Base response class
    """
    isSuccess = False
    errorMessages = []
    keyWords = []
    html = ''

    def __init__(self, nIsSuccess = None, nErrorMessages = None, nHmtl = None):
        if nIsSuccess is not None: self.isSuccess = nIsSuccess
        if nErrorMessages is not None: self.errorMessages = nErrorMessages
        if nHmtl is not None: self.html = nHmtl
