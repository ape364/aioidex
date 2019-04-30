class IdexDataStreamException(Exception):
    pass


class IdexDataStreamError(IdexDataStreamException):
    pass


class IdexHandshakeTimeout(IdexDataStreamException):
    pass


class IdexHandshakeException(IdexDataStreamException):
    pass


class IdexInvalidVersion(IdexDataStreamException):
    pass


class IdexAuthenticationFailure(IdexDataStreamException):
    pass


class IdexResponseSidError(IdexDataStreamException):
    pass


# HTTP API
class IdexClientException(Exception):
    pass


class IdexClientApiError(IdexClientException):
    pass


class IdexClientContentTypeError(IdexClientException):
    def __init__(self, status, content):
        self.status = status
        self.content = content

    def __str__(self):
        return f'[{self.status}] {self.content!r}'
