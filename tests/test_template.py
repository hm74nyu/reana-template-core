# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test TemplateSpec functionality."""


from unittest import TestCase

from reanatempl import TemplateSpec

import reanatempl.parameter.declaration as pd


class TestTemplateSpec(TestCase):
    def test_duplicate_id(self):
        """Ensure that exception is raised if parameter identifier are not
        unique.
        """
        with self.assertRaises(ValueError):
            TemplateSpec(
                workflow_spec={},
                parameters=[
                    pd.parameter_declaration('A', index=1),
                    pd.parameter_declaration('B'),
                    pd.parameter_declaration('C'),
                    pd.parameter_declaration('A', index=2),
                    pd.parameter_declaration('E', index=1)
                ],
                validate=True
            )

    def test_nested_parameters(self):
        """Test proper nesting of parameters for DT_LIST and DT_RECORD."""
        # Create a new TemplateSpec with an empty workflow specification and
        # a list of six parameters (one record and one list)
        template = TemplateSpec(
            workflow_spec={},
            parameters=[
                pd.parameter_declaration('A'),
                pd.parameter_declaration('B', data_type=pd.DT_RECORD),
                pd.parameter_declaration('C', parent='B'),
                pd.parameter_declaration('D', parent='B'),
                pd.parameter_declaration('E', data_type=pd.DT_LIST),
                pd.parameter_declaration('F', parent='E'),
            ],
            validate=True
        )
        # Parameters 'A', 'C', 'D', and 'F' have no children
        for key in ['A', 'C', 'D', 'F']:
            self.assertFalse(template.get_parameter(key).has_children())
        # Parameter 'B' has two children 'C' and 'D'
        b = template.get_parameter('B')
        self.assertTrue(b.has_children())
        self.assertEqual(len(b.children), 2)
        self.assertTrue('C' in [p.identifier for p in b.children])
        self.assertTrue('D' in [p.identifier for p in b.children])
        # Parameter 'E' has one childr 'F'
        e = template.get_parameter('E')
        self.assertTrue(e.has_children())
        self.assertEqual(len(e.children), 1)
        self.assertTrue('F' in [p.identifier for p in e.children])

    def test_simple_replace(self):
        """Replace parameter references in simple template with argument values.
        """
        template = TemplateSpec.load('tests/files/template.yaml')
        arguments = {'codeFile': 'Hello.py', 'sleeptime': 10}
        spec = template.get_workflow_spec(arguments)
        self.assertEqual(spec['inputs']['files'][0], 'Hello.py')
        self.assertEqual(spec['inputs']['parameters']['helloworld'], 'Hello.py')
        self.assertEqual(spec['inputs']['parameters']['sleeptime'], 10)
        self.assertEqual(spec['inputs']['parameters']['waittime'], 5)
        # Error when argument for mandatory parameter is missing
        with self.assertRaises(ValueError):
            template.get_workflow_spec(dict())
    def test_sort(self):
        """Test the sort functionality of the template list_parameters method.
        """
        # Create a new TemplateSpec with an empty workflow specification and
        # a list of five parameters
        template = TemplateSpec(
            workflow_spec={},
            parameters=[
                pd.parameter_declaration('A', index=1),
                pd.parameter_declaration('B'),
                pd.parameter_declaration('C'),
                pd.parameter_declaration('D', index=2),
                pd.parameter_declaration('E', index=1)
            ],
            validate=True
        )
        # Get list of sorted parameter identifier from listing
        keys = [p.identifier for p in template.list_parameter()]
        self.assertEqual(keys, ['B', 'C', 'A', 'E', 'D'])
