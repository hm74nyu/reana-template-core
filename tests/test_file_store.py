# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test simple file store functionality."""

import os
import shutil

from unittest import TestCase

from reanatempl.util.filestore import SimpleFileStore


LOCAL_FILE = 'tests/files/schema.json'
TMP_DIR = 'tests/.tmp'


class FakeStream(object):
    """Fake stream object to test upload from stream. Needs to implement the
    save(filename) function.
    """
    def save(self, filename):
        """Write simple text to given file."""
        with open(filename, 'w') as f:
            f.write('This is a fake\n')


class TestFilestore(TestCase):
    def setUp(self):
        """Create empty file store directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.mkdir(TMP_DIR)

    def tearDown(self):
        """Remove temporary file store directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_create_and_delete_file(self):
        """Test creating a new run resource for a template handle."""
        fs = SimpleFileStore(directory=TMP_DIR)
        # Create new entry from local file
        fh = fs.upload_file(LOCAL_FILE)
        self.assertTrue(os.path.isdir(os.path.join(TMP_DIR, fh.identifier)))
        self.assertTrue(os.path.isfile(fh.filepath))
        self.assertEqual(fh.name, 'schema.json')
        # Delete the uploaded file
        result = fs.delete_file(fh.identifier)
        self.assertTrue(result)
        self.assertFalse(os.path.isdir(os.path.join(TMP_DIR, fh.identifier)))
        self.assertFalse(os.path.isfile(fh.filepath))
        # Deleting a non existing file returns False
        result = fs.delete_file(fh.identifier)
        self.assertFalse(result)

    def test_upload_get_and_list_files(self):
        """Test uploading and accessing files for a run."""
        fs = SimpleFileStore(directory=TMP_DIR)
        fh1 = fs.upload_file(LOCAL_FILE)
        fh2 = fs.upload_file(LOCAL_FILE)
        # Both files have the same name but different identifier (and point to
        # different paths)
        self.assertNotEqual(fh1.identifier, fh2.identifier)
        self.assertNotEqual(fh1.filepath, fh2.filepath)
        self.assertEqual(fh1.name, fh2.name)
        # File listing contains two elements
        files = fs.list_files()
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0].name, files[1].name)
        self.assertNotEqual(files[0].identifier, files[1].identifier)
        self.assertNotEqual(files[0].filepath, files[1].filepath)
        # Recreate the file store and check that the two files still exist
        fs = SimpleFileStore(directory=TMP_DIR)
        files = fs.list_files()
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0].name, files[1].name)
        self.assertNotEqual(files[0].identifier, files[1].identifier)
        self.assertNotEqual(files[0].filepath, files[1].filepath)
        # Unpload unknown file will raise value error
        with self.assertRaises(ValueError):
            fs.upload_file('tests/files/thisisnotafile.noway')
        # Upload third file from stream
        fh = fs.upload_stream(FakeStream(), 'file.txt')
        self.assertEqual(len(fs.list_files()), 3)
        self.assertEqual(fh.name, 'file.txt')
        # Delete file
        fs.delete_file(fh.identifier)
        files = fs.list_files()
        self.assertEqual(len(files), 2)
        self.assertFalse(fh.identifier in [f.identifier for f in files])
        # Recreate the file store and check that only the two files still exist
        fs = SimpleFileStore(directory=TMP_DIR)
        files = fs.list_files()
        self.assertEqual(len(files), 2)
        self.assertFalse(fh.identifier in [f.identifier for f in files])
