# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Helper methods to read REANA Templates from file."""

import shutil
import uuid
import yaml


def copy_dir(src, dest, clean_up=None):
    """Copy a source folder to a destination folder. In case of an IOError
    delete the optinal clean-up directory.

    Parameters
    ----------
    src: string
        Path to source folder
    dest: string
        Path to destination folder
    clean_up: string, optional
        Path to clean-up folder that is removed in case of an error.
    """
    # Copy src folder to destination folder. Catch error if src or dest folder
    # is not found or cannot be copied. Remove clean-up folder on error (if
    # given).
    try:
        shutil.copytree(src, dest)
    except IOError as ex:
        # Make sure to cleanup by removing the optional folder
        if not clean_up is None:
            shutil.rmtree(clean_up)
        raise ex


def get_unique_identifier():
    """Create a new unique identifier.

    Returns
    -------
    string
    """
    return str(uuid.uuid4()).replace('-', '')


def get_short_identifier():
    """Create a unique identifier that contains only eigth characters. Uses the
    prefix of a unique identifier as the result.

    Returns
    -------
    string
    """
    return get_unique_identifier()[:8]


def load_template(filename):
    """Load a Json object from a file. The file may either be in Yaml or in Json
    format.

    Parameters
    ----------
    filename: string
        Path to file on disk

    Returns
    -------
    dict
    """
    with open(filename, 'r') as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
