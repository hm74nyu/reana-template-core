# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test functionality of token reader that are used by the scanner class."""

from unittest import TestCase

from reanatempl.util.scanner import TokenReader, ListReader


class TestTokenReader(TestCase):
    def test_abstract_reader(self):
        """The abstract reader class raises not implemented errors."""
        reader = TokenReader()
        with self.assertRaises(NotImplementedError):
            reader.next_token()

    def test_list_reader(self):
        """Test token reader that returns values from a given list."""
        reader = ListReader([3, 34.56, False, 'Some text'])
        self.assertEqual(reader.next_token(), '3')
        self.assertEqual(reader.next_token(), '34.56')
        self.assertEqual(reader.next_token(), 'False')
        self.assertEqual(reader.next_token(), 'Some text')
        # Reading past end of list will return Nne
        self.assertIsNone(reader.next_token())
