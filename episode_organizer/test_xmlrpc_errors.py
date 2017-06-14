import pytest

from episode_organizer.xmlrpc_errors import error_code, error


def test_error_code_ProvidesExpectedErrorClass_ReturnsCorrespondingCode():
    assert error_code(FileNotFoundError) == 1001


def test_error_code_ProvidesExpectedErrorClassInstance_ReturnsCorrespondingCode():
    assert error_code(FileNotFoundError()) == 1001


def test_error_code_ProvidesUnexpectedErrorClass_RaisesKeyError():

    class UnexpectedException(Exception):
        pass

    with pytest.raises(KeyError):
        error_code(UnexpectedException)


def test_error_ProvidesValidCode_ReturnsCorrespondingError():
    assert error(1001) == FileNotFoundError


def test_error_ProvidesInvalidErrorCode_RaisesKeyError():

    with pytest.raises(KeyError):
        error(1)
