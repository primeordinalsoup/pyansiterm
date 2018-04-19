import pytest
from ansiterm.ansiterm import *

def test_screen(capsys):
    """there is no easy way to automatically test
    this works so we just run the demo for visual
    confirmation.  also of course it exercises all
    the code and at least checks it does not assert
    etc."""
    demo()
    assert True

