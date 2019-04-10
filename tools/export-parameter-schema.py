# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Export the template parameter schema specification. Either prints the schema
to standard output or write to file if the optional file parameter is given.
"""

import getopt
import json
import sys
import yaml

from reanatempl.parameter.declaration import PARAMETER_SCHEMA


# Command line usage string
COMMAND = 'Usage: [-f <JSON|YAML> | --format=<JSON|YAML>] {output-file}'


def main(args, format):
    """Write template parameter declaration schema to file or standard output.

    Raise value error if invalid format is given.

    Parameters
    ----------
    args: list
        List of command line arguments. If the list is not empty only the first
        argument will be considered as the output file. If the argument list is
        empty the schema will be printed to standard output
    format: string
        Expects either YAML or JSON as the output format specification
    """
    if not format.upper() in ['YAML', 'JSON']:
        raise ValueError('invalid output format \'' + str(format) + '\'')
    if format.upper() == 'YAML':
        schema = yaml.dump(PARAMETER_SCHEMA, indent=4)
    else:
        schema = json.dumps(PARAMETER_SCHEMA, indent=4)
    # Output source depends on whether the output file argument is given or not
    if len(args) > 0:
        with open(args[0], 'w') as f:
            f.write(schema + '\n')
    else:
        print(schema)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:', ['format='])
        if len(args) > 1 or len(opts) > 1:
            print(COMMAND)
            sys.exit(-1)
        # If an option is given it is expected to contain a valid format (either
        # JSON or YAML). The default format is YAML.
        format = 'YAML'
        if len(opts) == 1:
            _, format = opts[0]
        if not format.upper() in ['YAML', 'JSON']:
            print('Invalid output format \'' + str(format) + '\'')
            print(COMMAND)
            sys.exit(-1)
        main(args=args, format=format)
    except getopt.GetoptError as ex:
        print(ex)
        sys.exit(-1)
