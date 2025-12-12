class BaseRequest(object):
    pass

class LocalRequest(BaseRequest):
    pass

Request = BaseRequest
request = LocalRequest()

class BaseResponse(object):
    pass

class LocalResponse(BaseResponse):
    pass

Response = BaseResponse
response = LocalResponse()

class HTTPResponse(Response, BottleException):
    pass

class HTTPError(HTTPResponse):
    pass
