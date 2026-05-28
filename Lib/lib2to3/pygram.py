# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Export the MyFRpy grammar and symbols."""

# MyFRpy imports
import os

# Local imports
from .pgen2 import token
from .pgen2 import driver
from . import pytree

# The grammar file
_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "Grammar.txt")
_PATTERN_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__),
                                     "PatternGrammar.txt")


class Symbols(object):

    def __init__(self, grammar):
        """Initializer.

        Creates an attribute for each grammar symbol (nonterminal),
        whose value is the symbol's type (an int >= 256).
        """
        for name, symbol in grammar.symbol2number.items():
            setattr(self, name, symbol)


myFRpy_grammar = driver.load_packaged_grammar("lib2to3", _GRAMMAR_FILE)

myFRpy_symbols = Symbols(myFRpy_grammar)

myFRpy_grammar_no_print_statement = myFRpy_grammar.copy()
del myFRpy_grammar_no_print_statement.keywords["print"]

myFRpy_grammar_no_print_and_exec_statement = myFRpy_grammar_no_print_statement.copy()
del myFRpy_grammar_no_print_and_exec_statement.keywords["exec"]

pattern_grammar = driver.load_packaged_grammar("lib2to3", _PATTERN_GRAMMAR_FILE)
pattern_symbols = Symbols(pattern_grammar)
