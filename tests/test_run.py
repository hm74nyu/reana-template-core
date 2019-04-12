# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test run handles for workflow templates."""

import os
import shutil

from unittest import TestCase

from reanatempl.template import TemplateHandle
from reanatempl.template import RUNS_FOLDER, SETTINGS_FILE


TMP_DIR = 'tests/.tmp'
WORKFLOW_DIR = 'tests/files/template'


class FakeStream(object):
    """Fake stream object to test upload from stream. Needs to implement the
    save(filename) function.
    """
    def save(self, filename):
        """Write simple text to given file."""
        with open(filename, 'w') as f:
            f.write('This is a fake\n')


class TestRunHandle(TestCase):
    def setUp(self):
        """Create empty template directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.mkdir(TMP_DIR)

    def tearDown(self):
        """Remove temporary template directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_create_and_delete_run(self):
        """Test creating a new run resource for a template handle."""
        th = TemplateHandle.create(workflow_dir=WORKFLOW_DIR, in_directory=TMP_DIR)
        # After creating the handle the runs folder does not exist
        runs_folder = os.path.join(th.directory, RUNS_FOLDER)
        self.assertFalse(os.path.isdir(runs_folder))
        run_id = th.create_run().identifier
        self.assertTrue(os.path.isdir(runs_folder))
        self.assertTrue(os.path.isdir(os.path.join(runs_folder, run_id)))
        # Delete the run
        th.delete_run(run_id)
        self.assertTrue(os.path.isdir(runs_folder))
        self.assertFalse(os.path.isdir(os.path.join(runs_folder, run_id)))
        # Delete run on a fresh template should not create the runs folder
        th = TemplateHandle.create(workflow_dir=WORKFLOW_DIR, in_directory=TMP_DIR)
        runs_folder = os.path.join(th.directory, RUNS_FOLDER)
        self.assertFalse(os.path.isdir(runs_folder))
        with self.assertRaises(ValueError):
            th.delete_run(run_id)
        self.assertFalse(os.path.isdir(runs_folder))
        # Get run with unknown identifier will return None
        self.assertIsNone(th.get_run('nonono'))

    def test_upload_and_list_files(self):
        """Test uploading and accessing files for a run."""
        th = TemplateHandle.create(workflow_dir=WORKFLOW_DIR, in_directory=TMP_DIR)
        rh = th.create_run()
        fh = rh.upload_file('tests/files/schema.json')
        self.assertEqual(fh.name, 'schema.json')
        fh = rh.get_file(fh.identifier)
        self.assertEqual(fh.name, 'schema.json')
        # Unknown file identifier will return None
        self.assertIsNone(rh.get_file('nonono'))
        self.assertEqual(len(rh.list_files()), 1)
        # Upload a second file
        fh = rh.upload_file('tests/files/schema.json')
        self.assertEqual(len(rh.list_files()), 2)
        # Both files have the same name but different identifier (and point to
        # different paths)
        files = rh.list_files()
        fh1 = files[0]
        fh2 = files[1]
        self.assertEqual(fh1.name, fh2.name)
        self.assertNotEqual(fh1.identifier, fh2.identifier)
        self.assertNotEqual(fh1.filepath, fh2.filepath)
        # Get the run handle and check files again
        rh = th.get_run(rh.identifier)
        files = rh.list_files()
        fh1 = files[0]
        fh2 = files[1]
        self.assertEqual(fh1.name, fh2.name)
        self.assertNotEqual(fh1.identifier, fh2.identifier)
        self.assertNotEqual(fh1.filepath, fh2.filepath)
        # Unpload unknown file will raise value error
        with self.assertRaises(ValueError):
            rh.upload_file('tests/files/thisisnotafile.noway')
        # Upload third file from stream
        fh = rh.upload_stream(FakeStream(), 'file.txt')
        self.assertEqual(len(rh.list_files()), 3)
        self.assertEqual(fh.name, 'file.txt')
