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
