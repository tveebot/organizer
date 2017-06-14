from functools import wraps
from inspect import isclass
from xmlrpc.client import Fault

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


def raise_faults(func):
    """
    This is supposed to be used as a decorator.
    All the exceptions raised by the decorated function are converted to Fault exceptions. If the raised error is
    included in the 'error_codes' list, then fault code will be set to the error code of that error. Otherwise,
    the exception is just re-raised and we let the xmlrpc library convert the exception to a Fault.
    """
    @wraps(func)
    def exception_to_fault(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except Exception as error:

            try:
                code = error_code(error)
                raise Fault(faultCode=code, faultString=str(error))

            except KeyError:
                raise error

    return exception_to_fault


def expect_faults(func):
    """
    This is supposed to be used as a decorator.
    All the Fault exceptions raised by the decorated function are converted to the corresponding errors based on the
    fault code. If the fault code is included in the 'error_codes' list, then the corresponding exception is
    raised with the error message included in the fault string. Otherwise, the Fault exception is re-raised. If the
    function raises an exception other than a Fault, then this exception is passed through.
    """
    @wraps(func)
    def fault_to_exception(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except Fault as fault:

            try:
                exception = error(fault.faultCode)
            except KeyError:
                raise fault

            raise exception(fault.faultString)

    return fault_to_exception
