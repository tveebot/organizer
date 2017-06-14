from inspect import isclass

from bidict import bidict


_error_codes = bidict({
    FileNotFoundError: 1001,
})


def error_code(error):
    """ Returns the error code for the given error. The error may be an exception class or instance. """

    if isclass(error):
        return _error_codes[error]
    else:
        return _error_codes[type(error)]


def error(error_code):
    """ Returns the error class corresponding to the given code """
    return _error_codes.inv[error_code]

