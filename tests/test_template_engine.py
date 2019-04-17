# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test basic functionality of the template engine (and the simple template
engine). None of the tests will actually run a workflow on an existing REANA
server.
"""

from unittest import TestCase

from reanatempl import TemplateSpec
from reanatempl.engine.base import TemplateEngine
from reanatempl.engine.alternate import SimpleTemplateEngine, get_request_url
from reanatempl.util.filestore import FileHandle

import reanatempl.parameter.declaration as pd


class FakeTemplateEngine(TemplateEngine):
    """Fake template engine for test purposes."""
    def __init__(self):
        self.started = False
        self.files = list()

    def create_workflow(self, workflow_spec, name=''):
        return 'ID'

    def upload_file(self, workflow_id, filename, target_file):
        self.files.append(target_file)

    def start_workflow(self, workflow_id):
        self.started = workflow_id == 'ID'


class TestTemplateEngine(TestCase):
    def test_get_request_url(self):
        """Test helper function to generate request Urls"""
        url = get_request_url(
            'http:/localhost///',
            '/api/ping/',
            {'workflow': 'ABC', 'token': 'XYZ'}
        )
        self.assertEqual(url, 'http:/localhost/api/ping?token=XYZ&workflow=ABC')

    def test_template_engine(self):
        """Test run method of template engine."""
        # Create a workflow template
        template = TemplateSpec(
            workflow_spec={'inputs': {'files': ['$[[fileA]]', '$[[fileB]]']}},
            parameters=[
                pd.parameter_declaration('fileA', data_type=pd.DT_FILE),
                pd.parameter_declaration('fileB', data_type=pd.DT_FILE, as_const='names.txt')
            ],
            validate=True
        )
        arguments = {
            'fileA': FileHandle('tests/files/template/code/helloworld.py'),
            'fileB': FileHandle('tests/files/template/inputs/names.txt')
        }
        engine = FakeTemplateEngine()
        engine.run(template, arguments, 'NAME')
        self.assertTrue(engine.started)
        self.assertEqual(len(engine.files), 2)
        self.assertTrue('helloworld.py' in engine.files)
        self.assertTrue('names.txt' in engine.files)
        # Value error when running a workflow with a missing upload file
        arguments = {
            'fileA': FileHandle('Hello.py'),
            'fileB': FileHandle('names.txt')
        }
        with self.assertRaises(ValueError):
            engine.run(template, arguments, 'NAME')
        engine = TemplateEngine()
        # For completeness test calling the abstract methods
        with self.assertRaises(NotImplementedError):
            engine.create_workflow(dict())
        with self.assertRaises(NotImplementedError):
            engine.upload_file('ID', '/dev/null', 'dev/null')
        with self.assertRaises(NotImplementedError):
            engine.start_workflow('ID')
