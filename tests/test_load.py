# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test loading REANA templates from file."""

import os

from unittest import TestCase

from reanatempl import TemplateSpec
from reanatempl.util.base import read_object, FORMAT_JSON, FORMAT_YAML

import reanatempl.parameter.declaration as pd


INVALID_JSON_FILE = 'tests/files/not-a-json-file.json'
INVALID_YAML_FILE = 'tests/files/not-a-yaml-file.yaml'


class TestLoadTemplate(TestCase):
    def test_load_invalid_file(self):
        """Test loading files that are not valid reana templates or that do not
        follow valid JSON or YAML syntax.
        """
        # Missing workflow specification
        with self.assertRaises(ValueError):
            TemplateSpec.load(os.path.abspath('tests/files/invalid-template1.yaml'))
        # Additional elements
        with self.assertRaises(ValueError):
            TemplateSpec.load(os.path.abspath('tests/files/invalid-template2.yaml'))
        # Value error when loading invalid JSON file
        with self.assertRaises(ValueError):
            read_object(INVALID_JSON_FILE, format=FORMAT_JSON)
        # Value error when loading invalid yaml file
        with self.assertRaises(ValueError):
            read_object(INVALID_YAML_FILE, format=FORMAT_YAML)

    def test_load_file(self):
        """Test loading files in either Yaml or Json format from disk using the
        read_object method.
        """
        # Load a Yaml file
        obj = read_object(os.path.abspath('tests/files/reana.yaml'))
        self.assertEqual(obj['version'], '0.3.0')
        # Load a Json file
        obj = read_object(
            os.path.abspath('tests/files/schema.json'),
            format=FORMAT_JSON
        )
        self.assertEqual(obj['type'], 'object')
        # Value error for invalid format argument
        with self.assertRaises(ValueError):
            read_object(os.path.abspath('tests/files/reana.yaml'), format='unk')

    def test_read_object_with_parameters(self):
        """Test loading a REANA workflow template that does contain template
        parameter declarations.
        """
        template = TemplateSpec.load('tests/files/template.yaml')
        self.assertTrue(isinstance(template.workflow_spec, dict))
        self.assertEqual(len(template.parameters), 3)
        # Code file parameter
        p_code = template.get_parameter('codeFile')
        self.assertEqual(p_code.name, 'Code File')
        self.assertEqual(p_code.data_type, pd.DT_FILE)
        self.assertEqual(p_code.as_constant, 'helloworld.py')
        # Sleep time parameter
        p_sleep = template.get_parameter('sleeptime')
        self.assertEqual(p_sleep.name, 'sleeptime')
        self.assertEqual(p_sleep.data_type, pd.DT_INTEGER)

    def test_load_simple_template(self):
        """Test loading a simple REANA workflow template that does not contain
        any template parameter.
        """
        template = TemplateSpec.load('tests/files/simple-template.yaml')
        self.assertTrue(isinstance(template.workflow_spec, dict))
        self.assertEqual(len(template.parameters), 0)
