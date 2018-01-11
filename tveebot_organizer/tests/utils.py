from pathlib import Path


def path_from(local_path) -> Path:
    return Path(str(local_path))


def assert_has_items(expected: list, items: list):
    """
    Asserts the *expected* list has the same items as the *items* list, in no
    particular order.
    """
    for item in items:
        assert item in expected
    assert len(expected) == len(items)
