# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Helper methods to read REANA Templates from file."""

import json
import uuid
import yaml


"""Unique identifier for supported data formats of template files."""
FORMAT_JSON = 'JSON'
FORMAT_YAML = 'YAML'


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


def load_template(filename, format=FORMAT_YAML):
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
    if format.upper() == FORMAT_YAML:
        with open(filename, 'r') as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)
    elif format.upper() == FORMAT_JSON:
        with open(filename, 'r') as f:
            return json.load(f.read())
    else:
        raise ValueError('unknown data format \'' + str(format) + '\'')

def write_json(filename, obj):
    """Write given dictionary to file as Json object.

    Parameters
    ----------
    filename: string
        Path to output file
    obj: dict
        Output object
    """
    with open(filename, 'w') as f:
        json.dump(obj, f)
