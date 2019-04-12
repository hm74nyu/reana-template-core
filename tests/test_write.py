# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test loading REANA templates from file."""

import os
import shutil

from unittest import TestCase

from reanatempl.util import write_object, FORMAT_JSON, FORMAT_YAML


TMP_DIR = 'tests/.tmp'


class TestWrite(TestCase):
    def setUp(self):
        """Create empty template directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.mkdir(TMP_DIR)

    def tearDown(self):
        """Remove temporary template directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_write_object(self):
        """Write object to file in JSON and YAML format."""
        obj = {'ABC': 1, 'EFG': 'xxx'}
        write_object(os.path.join(TMP_DIR, 'file.json'), obj, format=FORMAT_JSON)
        write_object(os.path.join(TMP_DIR, 'file.yml'), obj, format=FORMAT_YAML)
        files = os.listdir(TMP_DIR)
        self.assertTrue('file.json' in files)
        self.assertTrue('file.yml' in files)
        # Value error when providing invalid format
        with self.assertRaises(ValueError):
            write_object(os.path.join(TMP_DIR, 'file.yml'), obj, format='unk')
