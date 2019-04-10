# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Helper methods to read REANA Templates from file."""

import yaml


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
