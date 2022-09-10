"""
Things that simplify the testing process and help with it
"""

import re

import pytest


def fix_message(message: str):
    return "^" + re.escape(message).replace("\\ ", " ") + "$"


def raises_instance(exc: Exception):
    return pytest.raises(type(exc), match=fix_message(exc.args[0]))


def do_test(file: str) -> None:
    pytest.main([file, "-vv", "-W", "ignore::pytest.PytestAssertRewriteWarning"])
