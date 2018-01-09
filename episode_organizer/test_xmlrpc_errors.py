from xmlrpc.client import Fault

import pytest

from episode_organizer.xmlrpc_errors import error_code, error, raise_faults, expect_faults


class UnexpectedException(Exception):
    """ Represents an exception that is not defined in the expected errors """
    pass


def test_error_code_ProvidesExpectedErrorClass_ReturnsCorrespondingCode():
    assert error_code(FileNotFoundError) == 1001


def test_error_code_ProvidesExpectedErrorClassInstance_ReturnsCorrespondingCode():
    assert error_code(FileNotFoundError()) == 1001


def test_error_code_ProvidesUnexpectedErrorClass_RaisesKeyError():
    with pytest.raises(KeyError):
        error_code(UnexpectedException)


def test_error_ProvidesValidCode_ReturnsCorrespondingError():
    assert error(1001) == FileNotFoundError


def test_error_ProvidesInvalidErrorCode_RaisesKeyError():
    with pytest.raises(KeyError):
        error(1)


def test_raise_faults_FunctionRaisesExpectedError_RaisesFaultWithCorrespondingCodeAndMessage():
    @raise_faults()
    def raising_func():
        raise FileNotFoundError("error message")

    with pytest.raises(Fault) as exception_info:
        raising_func()

    assert exception_info.value.faultCode == 1001
    assert exception_info.value.faultString == "error message"


def test_raise_faults_FunctionDoesNotRaiseException_DoesNotRaiseException():
    @raise_faults()
    def non_raising_func():
        pass  # does not raise anything

    non_raising_func()


def test_raise_faults_FunctionRaisesUnexpectedError_RaisesTheUnexpectedError():
    @raise_faults()
    def raising_func():
        raise UnexpectedException("error message")

    with pytest.raises(UnexpectedException):
        raising_func()


def test_expect_faults_FaultWithValidCode_RaisesCorrespondingExceptionWithTheFaultMessage():
    @expect_faults()
    def raising_func():
        raise Fault(faultCode=1001, faultString="error message")

    with pytest.raises(FileNotFoundError) as exception_info:
        raising_func()

    assert str(exception_info.value) == "error message"


def test_expect_faults_FunctionRaisesUnexpectedError_RaisesTheUnexpectedError():
    @expect_faults()
    def non_raising_func():
        pass  # does not raise anything

    non_raising_func()


def test_expect_faults_FunctionRaisesExceptionNotFault_RaisesTheException():
    @expect_faults()
    def non_raising_func():
        raise Exception()

    with pytest.raises(Exception):
        non_raising_func()


def test_expect_faults_FaultWithInvalidCode_RaisesSameFaultError():
    @expect_faults()
    def raising_func():
        raise Fault(faultCode=1, faultString="error message")

    with pytest.raises(Fault) as exception_info:
        raising_func()

    assert exception_info.value.faultCode == 1
    assert exception_info.value.faultString == "error message"


def test_expect_faults():
    with pytest.raises(FileNotFoundError) as exception_info:
        with expect_faults():
            raise Fault(faultCode=1001, faultString="error message")

    assert str(exception_info.value) == "error message"
