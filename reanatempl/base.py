# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""REANA Template class. A REANA template has two main components: (1) a REANA
workflow declaration and (2) a list of optional template parameters.

The workflow declaration may contain references to template parameters. The
template parameters are for example used to render front-end forms for parameter
input. Given an association of parameter identifier with values we use this to
create a valid REANA workflow specification by replacing the references to
template  parameters with the respective values in the value dictionary.
"""

from __future__ import print_function

import os

from reanatempl.parameter.base import TemplateParameter
from reanatempl.util.base import read_object
from reanatempl.util.filestore import FileHandle
from reanatempl.util.scanner import Scanner

import reanatempl.parameter.declaration as pd


"""Labels for top-level elements in REANA Templates."""
LABEL_PARAMETERS = 'parameters'
LABEL_TEMPLATE = 'template'


class TemplateSpec(object):
    """A REANA workflow template contains a REANA workflow specification and
    a dictionary of template parameter declarations. Parameter declarations are
    keyed by their unique identifier in the dictionary.
    """
    def __init__(self, workflow_spec, parameters=None, validate=False):
        """Initialize the workflow specification and the list of template
        parameter declaration. Template parameters are optional.

        If the valid flag is True all given template parameter declarations are
        validated against the parameter schema. Raises ValueError if any of
        the given parameter declarations fails the validation.

        Raises ValueError if the identifier for the given parameter declarations
        are not unique.

        Parameters
        ----------
        workflow_spec: dict
            Json object containing a REANA workflow specification
        parameters: list, optional
            List of workflow template parameter declarations
        validate: bool, optional
            Flag indicating if given template parameter declarations are to be
            validated against the parameter schema or not.
        """
        self.workflow_spec = workflow_spec
        # Add given parameter declaration to the parameters list. Ensure that
        # all default values are set
        self.parameters = dict()
        if not parameters is None:
            for para in parameters:
                # Validate the template parameters if the validate flag is True
                if validate:
                    pd.validate_parameter(para)
                # Create a TemplateParameter instance for the parameter. Keep
                # track of children for parameter that are of type DT_LIST or
                # DT_RECORD. Childrens are added after all parameters have been
                # instantiated.
                p_id = para[pd.LABEL_ID]
                # Raise ValueError if the parameter identifier is not unique
                if p_id in self.parameters:
                    raise ValueError('parameter \'' + str(p_id) + '\'  not unique')
                c = None
                if para[pd.LABEL_DATATYPE] in [pd.DT_LIST, pd.DT_RECORD]:
                    c = list()
                tp = TemplateParameter(pd.set_defaults(para), children=c)
                self.parameters[p_id] = tp
            # Add parameter templates to the list of children for their
            # respective parent (if given). We currently only support one level
            # of nesting.
            for para in parameters:
                if pd.LABEL_PARENT in para:
                    p_id = para[pd.LABEL_ID]
                    parent = para[pd.LABEL_PARENT]
                    if not parent is None:
                        self.parameters[parent].add_child(self.parameters[p_id])

    @staticmethod
    def from_dict(obj, validate=True):
        """Create an instance of the template specification from a given
        dictionary serialization. Expects a dictionary as created by the
        .to_dict() method of this class.

        Raises ValueError if an invalid dictionary is given.

        Parameters
        ----------
        obj: dict
            Dictionary serialization of a template specification

        Returns
        -------
        reanatempl.TemplateSpec
        -----
        """
        # Ensure that the Json object contains at least the 'template' element
        # and at most 'template' and 'parameter' elements
        if not LABEL_TEMPLATE in obj:
            raise ValueError('missing element \'' + LABEL_TEMPLATE + '\'')
        for key in obj:
            if not key in [LABEL_TEMPLATE, LABEL_PARAMETERS]:
                raise ValueError('invalid element \'' + str(key) + '\'')
        # Return new REANA Template object
        return TemplateSpec(
            obj.get(LABEL_TEMPLATE),
            parameters=obj.get(LABEL_PARAMETERS),
            validate=validate
        )

    def get_parameter(self, identifier):
        """Short-cut to access the declaration for a parameter with the given
        identifier.

        Parameters
        ----------
        identifier: string
            Unique parameter declaration identifier

        Returns
        -------
        dict
        """
        return self.parameters.get(identifier)

    def get_upload_files(self, arguments, ensure_file_exists=False):
        """Get list of files that are defined in the inputs.files section of the
        workflow specification. Replaces references to template parameters with
        references to values in the arguments dictionary.

        Raises ValueError if the ensure_file_exists flag is True and any of the
        local upload files does not exist.

        Parameters
        ----------
        arguments: dict
            Dictionary that associates template parameter identifiers with
            argument values
        ensure_file_exists: bool, optional
            Flag indicating whether existence of upload files if checked

        Returns
        -------
        list(reanatempl.base.UploadFileHandle)
        """
        files = list()
        # Ensure that the inputs.files element exists in the workflow
        # specification
        if 'inputs' in self.workflow_spec:
            if 'files' in self.workflow_spec['inputs']:
                for value in self.workflow_spec['inputs']['files']:
                    upload_handle = None
                    if is_parameter(value):
                        var = get_parameter_name(value)
                        para = self.get_parameter(var)
                        if para is None:
                            raise ValueError('unknwon parameter \'' + var + '\'')
                        fh = arguments.get(var)
                        if fh is None:
                            raise ValueError('missing value for parameter \'' + var + '\'')
                        if para.has_constant():
                            target_file = para.get_constant()
                        else:
                            target_file = fh.name
                        upload_handle = UploadFileHandle(
                            filename=fh.filepath,
                            target_file=target_file
                        )
                    else:
                        upload_handle = UploadFileHandle(filename=value)
                    if ensure_file_exists and not os.path.exists(upload_handle.filename):
                        raise ValueError('file \'' + upload_handle.filename + '\' does not exist')
                    files.append(upload_handle)
        return files

    def get_workflow_spec(self, arguments):
        """Get REANA workflow specification where template parameters are
        replaced by the given arguments.

        Raises ValueError if for any of the mandatory template parameters no
        value is given in the arguments dictionary (and no default value is
        defined in the parameter declaration).

        Parameters
        ----------
        arguments: dict
            Dictionary that associates template parameter identifiers with
            argument values

        Returns
        -------
        dict
        """
        # Raise ValueError if a parameter is required and no argument is given
        # or default value defined
        for para in self.parameters.values():
            if para.is_required and para.default_value is None:
                if not para.identifier in arguments:
                    raise ValueError('missing value for mandatory parameter \'' + str(para.identifier) + '\'')
        # Replace template parameter references in the workflow specification
        # with respective values in the argument dictionary or their defined
        # default value
        return replace_args(self.workflow_spec, arguments, self.parameters)

    def list_parameters(self):
        """Get a sorted list of parameter declarations. Elements are sorted by
        their index value. Ties are broken using the unique parameter
        identifier.

        Returns
        -------
        list
        """
        params = self.parameters.values()
        return sorted(params, key=lambda p: (p.index, p.identifier))

    @staticmethod
    def load(filename, validate=True):
        """Load REANA workflow template declaration from file and return an
        instance of the TemplateSpec class.

        Raises ValueError if the file does not contain a valid workflow
        template.

        Parameters
        ----------
        filename: string
            Path to file containing the REANA workflow template declaration
        validate: bool, optional
            Flag indicating whether parameter declarations in the template
            should be validated or not

        Returns
        -------
        reanatempl.base.TemplateSpec
        """
        # Load Json object from given file and create a specification instance
        # from the read object
        return TemplateSpec.from_dict(read_object(filename), validate=validate)

    def read(self, scanner=None):
        """Read values for each of the template parameter using a given input
        scanner. If no scanner is given values are read from standard input.

        Returns a dictionary of argument values that can be passed to the
        get_workflow_spec() method to get a valid REANA workflow specification.

        Parameters
        ----------
        scanner: reanatempl.util.scanner.Scanner
            Input scanner to read parameter values

        Returns
        -------
        dict
        """
        sc = scanner if not scanner is None else Scanner()
        arguments = dict()
        for para in self.list_parameters():
            # Skip nested parameter
            if not para.parent is None:
                continue
            if para.is_list():
                raise ValueError('lists are not supported yet')
            elif para.is_record():
                # A record can only appear once and all record children have
                # global unique identifier. Thus, we can add values for each
                # of the children directly to the arguments dictionary
                print(para.name)
                for child in para.children:
                    val = self.read_parameter(child, sc, prompt_prefix='  ')
                    if not val is None:
                        arguments[child.identifier] = val
            else:
                val = self.read_parameter(para, sc)
                if not val is None:
                    arguments[para.identifier] = val
        return arguments

    def read_parameter(self, para, scanner, prompt_prefix=''):
        """Read value for a given template parameter declaration. Prompts the
        user to enter a value for the given parameter and returns the converted
        value that was entered by the user.

        Parameters
        ----------
        para: reanatempl.parameter.TemplateParameter
            REANA workflow template parameter declaration

        Returns
        -------
        bool or float or int or string or list
        """
        done = False
        while not done:
            done = True
            print(prompt_prefix + para.prompt(), end='')
            try:
                if para.is_bool():
                    return scanner.next_bool(default_value=para.default_value)
                elif para.is_file():
                    filename = scanner.next_file(default_value=para.default_value)
                    return FileHandle(filepath=filename)
                elif para.is_float():
                    return scanner.next_float(default_value=para.default_value)
                elif para.is_int():
                    return scanner.next_int(default_value=para.default_value)
                else:
                    return scanner.next_string(default_value=para.default_value)
            except ValueError as ex:
                print(ex)
                done = False

    def to_dict(self):
        """Return dictionary serialization for the workflow template object.

        Returns
        -------
        dict
        """
        return {
            LABEL_TEMPLATE: self.workflow_spec,
            LABEL_PARAMETERS: [p.to_dict() for p in self.parameters.values()]
        }


# ------------------------------------------------------------------------------
# Helper Classes and Methods
# ------------------------------------------------------------------------------

class UploadFileHandle(object):
    """Handle for an input file to the workflow that needs to be uploaded to
    the REANA server before workflow execution is started. This class is a
    simple wrapper for a reference to a local file and a target file path.
    """
    def __init__(self, filename, target_file=None):
        """Initialize the filename and upload target path. If the target path is
        missing it is set to the value of the filename.

        Parameters
        ----------
        filename: string
            Path to the local file
        target_file: string, optional
            Target path for uploaded file on server. This path is relative to
            the working directory of the created workflow
        """
        self.filename = os.path.abspath(filename)
        self.target_file = target_file if not target_file is None else filename


def is_parameter(value):
    """Returns True if the given value is a reference to a template parameter.

    Parameters
    ----------
    value: string
        String value in the workflow specification for a REANA template

    Returns
    -------
    bool
    """
    # Check if the value matches the template parameter reference pattern
    return value.startswith('$[[') and value.endswith(']]')


def get_parameter_name(value):
    """Extract the parameter name for a template parameter reference.

    Parameters
    ----------
    value: string
        String value in the workflow specification for a REANA template

    Returns
    -------
    string
    """
    return value[3:-2]


def replace_args(spec, arguments, parameters):
    """Replace template parameter references in the workflow specification
    dictionary with their respective values in the argument dictionary or their
    defined default value.

    Returns a modified dictionary.

    Parameters
    ----------
    spec: dict
        (Part of the) workflow specification for a REANA template
    arguments: dict
        Dictionary that associates template parameter identifiers with
        argument values
    parameters: dict(reanatempl.parameter.TemplateParameter)
        Dictionary of parameter declarations for a REANA template

    Returns
    -------
    dict
    """
    # The new object will contain the modified workflow specification
    obj = dict()
    for key in spec:
        val = spec[key]
        # Modify the value that is currently associated with key according to
        # the value type
        if isinstance(val, str):
            # If the value is of type string we need to test whether the string
            # is a reference to a template parameter and (if True) replace the
            # value with the given argument or default value.
            val = replace_value(val, arguments, parameters)
        elif isinstance(val, dict):
            # Recursive call to replace_args if the value is a dictionary
            val = replace_args(val, arguments, parameters)
        elif isinstance(val, list):
            # Create modified list where each list element is modified depending
            # on its type.
            modified_list = list()
            for list_val in val:
                if isinstance(list_val, str):
                    # Replace potential references to template parameters in
                    # list elements of type string.
                    list_val = replace_value(list_val, arguments, parameters)
                elif isinstance(list_val, dict):
                    # Recursive replace for dictionaries
                    list_val = replace_args(list_val, arguments, parameters)
                elif isinstance(list_val, list):
                    # We currently do not support lists of lists
                    raise ValueError('nested lists not supported')
                modified_list.append(list_val)
            val = modified_list
        # If the modified value is null the key is omitted from the resulting
        # workflow specification
        if not val is None:
            obj[key] = val
    return obj


def replace_value(value, arguments, parameters):
    """Test whether the string is a reference to a template parameter and (if
    True) replace the value with the given argument or default value.

    In the current implementation template parameters are referenced using
    $[[..]] syntax.

    Parameters
    ----------
    value: string
        String value in the workflow specification for a REANA template
    arguments: dict
        Dictionary that associates template parameter identifiers with
        argument values
    parameters: dict(reanatempl.parameter.TemplateParameter)
        Dictionary of parameter declarations for a REANA template

    Returns
    -------
    string
    """
    # Check if the value matches the template parameter reference pattern
    if is_parameter(value):
        # Extract variable name.
        var = get_parameter_name(value)
        para = parameters[var]
        # If the parameter has a constant value defined use that value as the
        # replacement
        if para.has_constant():
            return para.get_constant()
        # If arguments contains a value for the variable we return the
        # associated value from the dictionary. Note that there is a special
        # treatment for file arguments. If case of file arguments the dictionary
        # value is expected to be a file handle. In this case we return the
        # file name as the argument value.
        if var in arguments:
            arg = arguments[var]
            if para.is_file():
                return arg.name
            else:
                return arg
        # Return the parameter default value
        return para.default_value
    else:
        return value
