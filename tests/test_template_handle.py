# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test creating and loading template handles."""

import os
import shutil

from unittest import TestCase

from reanatempl.handle import TemplateHandle, read_template_file, BACKEND, SETTINGS_FILE

REPO_URL = 'https://github.com/hm74nyu/reana-template-helloworld-demo.git'
TEMPLATE_FILE = 'tests/files/template.yaml'
TMP_DIR = 'tests/.tmp'
WORKFLOW_DIR = 'tests/files/template'


def fake_id_func():
    """Fake identifier function that always returns '0000'."""
    return '0000'


class TestTemplateHandle(TestCase):
    def setUp(self):
        """Create empty template directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.mkdir(TMP_DIR)

    def tearDown(self):
        """Remove temporary template directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_create_handle_from_dir(self):
        """Test creating template handle from directory."""
        th = TemplateHandle.create(workflow_dir=WORKFLOW_DIR, in_directory=TMP_DIR)
        template = th.get_template_spec()
        self.assertTrue(isinstance(template.workflow_spec, dict))
        self.assertEqual(len(template.parameters), 3)
        for para in ['names', 'sleeptime', 'waittime']:
            self.assertTrue(para in template.parameters)
        identifier = os.path.basename(th.directory)
        self.assertEqual(th.identifier, identifier)
        self.assertEqual(th.name, identifier)
        self.assertIsNone(th.description)
        self.assertTrue(os.path.isfile(os.path.join(th.directory, SETTINGS_FILE)))
        # Create template with custom identifier and name
        th = TemplateHandle.create(
            identifier='ABC',
            name='My Name',
            description='A long description',
            backend=BACKEND(serverUrl='url', accessToken='token'),
            workflow_dir=WORKFLOW_DIR,
            in_directory=TMP_DIR
        )
        identifier = os.path.basename(th.directory)
        self.assertNotEqual(th.identifier, identifier)
        self.assertEqual(th.identifier, 'ABC')
        self.assertEqual(th.name, 'My Name')
        self.assertEqual(th.description, 'A long description')

    def test_create_handle_from_repo(self):
        """Test creating template handle from a GitHub repository."""
        th = TemplateHandle.create(workflow_repo_url=REPO_URL, in_directory=TMP_DIR)
        template = th.get_template_spec()
        self.assertTrue(isinstance(template.workflow_spec, dict))
        self.assertEqual(len(template.parameters), 3)
        for para in ['names', 'sleeptime', 'waittime']:
            self.assertTrue(para in template.parameters)
        identifier = os.path.basename(th.directory)
        self.assertEqual(th.identifier, identifier)
        self.assertEqual(th.name, identifier)
        self.assertIsNone(th.description)
        self.assertTrue(os.path.isfile(os.path.join(th.directory, SETTINGS_FILE)))

    def test_invalid_arguments(self):
        """Ensure that ValueErrors are raised when invalid arguments are given
        to the create method.
        """
        with self.assertRaises(ValueError):
            TemplateHandle.create()
        with self.assertRaises(ValueError):
            TemplateHandle.create(workflow_dir=TMP_DIR, workflow_repo_url='')
        with self.assertRaises(ValueError):
            TemplateHandle.create(workflow_dir=TMP_DIR, backend={'serverUrl': 'ABC'})
        with self.assertRaises(ValueError):
            TemplateHandle.create(workflow_dir=TMP_DIR, backend={'serverUrl': 'ABC', 'noName': 1})
        with self.assertRaises(ValueError):
            TemplateHandle.create(workflow_dir=TMP_DIR, in_directory='@#$%^&*()')
        with self.assertRaises(ValueError):
            TemplateHandle.create(workflow_dir='@#$%^&*()', in_directory=TMP_DIR)
        self.assertEqual(len(os.listdir(TMP_DIR)), 0)
        os.mkdir(os.path.join(TMP_DIR, fake_id_func()))
        # This should reach max attempta and raise a ValueError
        with self.assertRaises(ValueError):
            TemplateHandle.create(workflow_dir=WORKFLOW_DIR, in_directory=TMP_DIR, id_func=fake_id_func)
        # Test BACKEND helper arguments
        with self.assertRaises(ValueError):
            BACKEND(None, 'ABC')
        with self.assertRaises(ValueError):
            BACKEND('ABC', None)

    def test_read_template_file(self):
        """Test finding and reading a template file in a given directory."""
        # Find the default file
        for name in ['reana-template', 'reana_template', 'template', 'workflow']:
            for suffix in ['yml', 'yaml']:
                target = name + '.' + suffix
                directory = os.path.join(TMP_DIR, 'tmp')
                os.mkdir(directory)
                shutil.copy(TEMPLATE_FILE, os.path.join(directory, target))
                template = read_template_file(directory)
                self.assertTrue(isinstance(template.workflow_spec, dict))
                self.assertEqual(len(template.parameters), 3)
                shutil.rmtree(directory)
        shutil.copy(TEMPLATE_FILE, os.path.join(TMP_DIR, 'somefile'))
        template = read_template_file(TMP_DIR, filename='somefile')
        self.assertTrue(isinstance(template.workflow_spec, dict))
        self.assertEqual(len(template.parameters), 3)
        with self.assertRaises(ValueError):
            read_template_file(TMP_DIR)
