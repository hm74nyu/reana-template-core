# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test  functionality of the basic template store that is shipped with the
package.
"""

import os
import shutil

from unittest import TestCase

from reanatempl.util.template.store import TemplateStore


TMP_DIR = 'tests/.tmp'
WORKFLOW_DIR = 'tests/files/template'


class TestTemplateStore(TestCase):
    def setUp(self):
        """Create empty template store directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.mkdir(TMP_DIR)

    def tearDown(self):
        """Remove temporary template store directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_delete_error(self):
        """Ensure that a ValueError is raised if the directory of a template
        that is being deleted does not exist.
        """
        store = TemplateStore(directory=TMP_DIR)
        th = store.add_template(
            name='My Template',
            description='This is the first template',
            workflow_dir=WORKFLOW_DIR
        )
        # Delete template directory
        shutil.rmtree(th.directory)
        with self.assertRaises(ValueError):
            store.delete_template(th.identifier)
            
    def test_template_life_cycle(self):
        """Test creating, accessing, listing and deleting templates."""
        store = TemplateStore(directory=TMP_DIR)
        th = store.add_template(
            name='My Template',
            description='This is the first template',
            workflow_dir=WORKFLOW_DIR
        )
        self.assertEqual(len(store.list_templates()), 1)
        self.validate_template_handle(th)
        # Get template and repeat tests
        th = store.get_template(th.identifier)
        self.validate_template_handle(th)
        # Re-create store, get template and repeat tests
        store = TemplateStore(directory=TMP_DIR)
        th = store.get_template(th.identifier)
        self.validate_template_handle(th)
        self.assertEqual(len(store.list_templates()), 1)
        # Add another template
        th = store.add_template(
            name='My Second Template',
            workflow_dir=WORKFLOW_DIR
        )
        self.assertEqual(th.name, 'My Second Template')
        self.assertIsNone(th.description)
        self.assertEqual(len(store.list_templates()), 2)
        # Delete template
        self.assertTrue(store.delete_template(th.identifier))
        self.assertFalse(store.delete_template(th.identifier))
        self.assertEqual(len(store.list_templates()), 1)
        # Get non-existing template returns None
        self.assertIsNone(store.get_template(th.identifier))
        # Re-create the store instance and delete the remaining template
        store = TemplateStore(directory=TMP_DIR)
        self.assertEqual(len(store.list_templates()), 1)
        th = store.list_templates()[0]
        self.assertTrue(store.delete_template(th.identifier))
        self.assertFalse(store.delete_template(th.identifier))
        self.assertEqual(len(store.list_templates()), 0)

    def validate_template_handle(self, th):
        """Basic tests to validate a given template handle
        """
        self.assertEqual(th.name, 'My Template')
        self.assertEqual(th.description, 'This is the first template')
        spec = th.get_template_spec()
        self.assertEqual(len(spec.parameters), 3)
