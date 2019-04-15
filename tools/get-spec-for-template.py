# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Get REANA workflow specification for a given workflow template. Propmpts user
to enter values for all template parameters. Write workflow specification either
to standard output or to a given output file.
"""

import getopt
import sys
import yaml

from reanatempl import TemplateSpec
from reanatempl.util.base import write_object


# Command line usage string
COMMAND = 'Usage: {[-o | --output=] <output-file>} <template-file>'


def main(input_file, output_file=None):
    """Prompt user to input values for all template parameters. Write workflow
    specification with replaced template parameter arguments either to standard
    output or to the given output file.

    Parameters
    ----------
    input_file: string
        Path to REANA workflow template specification file
    output_file: string, optional
        Optional path to output file
    """
    # Read the workflow template specification file
    template = TemplateSpec.load(filename=input_file)
    # Get the workflow specification. Will prompt the user to input parameter
    # values via standard input.
    workflow_spec = template.get_workflow_spec(template.read())
    # Depending on whether an output file is given or not the workflow
    # specification is either written to file or to standar output.
    if not output_file is None:
        write_object(output_file, workflow_spec)
    else:
        print(yaml.dump(workflow_spec))


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'o:', ['output='])
        if len(args) != 1:
            print(COMMAND)
            sys.exit(-1)
        # Set output file if the user provided a value for the respective
        # command line option.
        output_file = None
        if len(opts) == 1:
            _, output_file = opts[0]
        main(input_file=args[0], output_file=output_file)
    except getopt.GetoptError as ex:
        print(ex)
        sys.exit(-1)
