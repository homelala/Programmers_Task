class ApiError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self, debug=True):
        rv = dict(message=self.message)
        if debug and self.payload:
            rv.update(self.payload)
        if debug and self.__cause__:
            rv["cause"] = str(self.__cause__)
        return rv