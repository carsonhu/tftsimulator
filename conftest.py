"""Make pytest resolve this set's modules rather than the parent folder's.

`set17/__init__.py` makes this directory a package, so pytest's default
"prepend" import mode walks up past it and puts the PARENT (tft_calculator/) on
sys.path instead of this directory. That parent still contains the set-5-era
champion.py, status.py and buffs.py, so `import champion` inside a test picked
up a Champion whose __init__ predates the `role` argument -- every test in this
folder failed with "takes 10 positional arguments but 11 were given" and had
been doing so silently.

Putting this directory ahead of the parent makes the tests import the same
modules the app does.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
