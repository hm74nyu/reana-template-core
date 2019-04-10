# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test read arguments function for REANA templates."""


from unittest import TestCase

from reanatempl import REANATemplate
from reanatempl.scanner import Scanner, ListReader


class TestReadTemplateArguments(TestCase):
    def test_read_with_record(self):
        """Read argument for a template that contains a parameter of data type
        DT_RECORD.
        """
        template = REANATemplate.load('reanatempl/tests/files/template_with_record.yaml')
        sc = Scanner(reader=ListReader(['ABC.txt', 3, True, 'XYZ.txt', 6, 0.123]))
        arguments = template.read(scanner=sc)
        self.assertEqual(arguments['codeFile'], 'ABC.txt')
        self.assertEqual(arguments['sleeptime'], 3)
        self.assertEqual(arguments['verbose'], True)
        self.assertEqual(arguments['outputTarget'], 'XYZ.txt')
        self.assertEqual(arguments['outputType'], 6)
        self.assertEqual(arguments['frac'], 0.123)
