#!/usr/bin/env python3
"""Classes and methods for working with all Turing machines."""

import abc

import automata.base.exceptions as exceptions
from automata.base.automaton import Automaton


class TM(Automaton, metaclass=abc.ABCMeta):
    """An abstract lexer class for Turing machines."""

    def _read_input_symbol_subset(self):
        if not (self.input_symbols < self.tape_symbols):
            raise exceptions.MissingSymbolError(
                'The set of tape symbols is missing symbols from the input '
                'symbol set ({})'.format(
                    self.tape_symbols - self.input_symbols))

    def _validate_nonfinal_initial_state(self):
        """Raise an error if the initial state is a final state."""
        if self.initial_state in self.final_states:
            raise exceptions.InitialStateError(
                'initial state {} cannot be a final state'.format(
                    self.initial_state))
