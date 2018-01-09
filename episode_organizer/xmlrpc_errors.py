from contextlib import ContextDecorator
from functools import wraps
from inspect import isclass
from xmlrpc.client import Fault

from bidict import bidict

_error_codes = bidict({
    FileNotFoundError: 1001,
    OSError: 1002,
})


def error_code(error):
    """
    Returns the error code for the given error. The error may be an exception class or instance.
    """

    if isclass(error):
        return _error_codes[error]
    else:
        return _error_codes[type(error)]


def error(error_code):
    """ Returns the error class corresponding to the given code """
    return _error_codes.inv[error_code]


class raise_faults:
    """
    This is supposed to be used as a decorator or a context manager.

    All the exceptions raised by the decorated function (or context) are converted to Fault
    exceptions. If the raised error is included in the 'error_codes' list, then fault code will
    be set to the error code of that error. Otherwise, the exception is just re-raised and we let
    the xmlrpc library convert the exception to a Fault.
    """

    def __call__(self, func):

        @wraps(func)
        def exception_to_fault(*args, **kwargs):

            try:
                return func(*args, **kwargs)

            except Exception as exception:
                self.exception_to_fault(exception)

        return exception_to_fault

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exception_to_fault(exc_val)

    @staticmethod
    def exception_to_fault(exception):

        try:
            code = error_code(exception)
            raise Fault(faultCode=code, faultString=str(exception))

        except KeyError:
            raise exception


class expect_faults(ContextDecorator):
    """
    This is supposed to be used as a decorator or a context manager.

    All the Fault exceptions raised by the decorated function (context) are converted to the
    corresponding errors based on the fault code. If the fault code is included in the
    'error_codes' list, then the corresponding exception is raised with the error message
    included in the fault string. Otherwise, the Fault exception is re-raised. If the
    function/context raises an exception other than a Fault, then this exception is passed through.
    """

    def __call__(self, func):

        @wraps(func)
        def fault_to_exception(*args, **kwargs):

            try:
                return func(*args, **kwargs)

            except Fault as fault:
                self.fault_to_exception(fault)

        return fault_to_exception

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fault_to_exception(exc_val)

    @staticmethod
    def fault_to_exception(fault):

        try:
            exception = error(fault.faultCode)
        except KeyError:
            raise fault

        raise exception(fault.faultString)
