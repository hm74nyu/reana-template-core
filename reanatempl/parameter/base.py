# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Base class definitions to work with template parameters."""

import reanatempl.parameter.declaration as pd


class TemplateParameter(object):
    """The template parameter class is a simple wrapper around a dictionary that
    contains a parameter declaration. The wrapper provides easy access to the
    diccerent components of the parameter declaration.
    """
    def __init__(self, obj, children=None):
        """Initialize the different attributes of a template parameter
        declaration from the given dictionary.

        Parameters
        ----------
        obj: dict
            Dictionary containing the template parameter declaration properties
        children: list(reanatempl.parameter.TemplateParameter), optional
            Optional list of parameter children for parameter lists or records
        """
        self.obj = obj
        self.identifier = obj[pd.LABEL_ID]
        self.name = obj[pd.LABEL_NAME]
        self.data_type = obj[pd.LABEL_DATATYPE]
        self.description = obj[pd.LABEL_DESCRIPTION]
        self.index = obj[pd.LABEL_INDEX]
        self.default_value = obj[pd.LABEL_DEFAULT] if pd.LABEL_DEFAULT in obj else None
        self.is_required = obj[pd.LABEL_REQUIRED]
        self.values = obj[pd.LABEL_VALUES] if pd.LABEL_VALUES in obj else None
        self.parent = obj[pd.LABEL_PARENT] if pd.LABEL_PARENT in obj else None
        self.children = children

    def add_child(self, para):
        """Short-cut to add an element to the list of child parameter.

        Parameters
        ----------
        para: reanatempl.parameter.TemplateParameter
            Template parameter instance for child parameter
        """
        self.children.append(para)
        self.children.sort(key=lambda p: (p.index, p.identifier))

    def has_children(self):
        """Test if a parameter has children. Only returns True if the list of
        children is not None and not empty.

        Returns
        -------
        bool
        """
        if not self.children is None:
            return len(self.children) > 0
        return False

    def is_bool(self):
        """Test if data type for the parameter declaration is DT_BOOL.

        Returns
        -------
        bool
        """
        return self.data_type == pd.DT_BOOL

    def is_file(self):
        """Test if data type for the parameter declaration is DT_FILE.

        Returns
        -------
        bool
        """
        return self.data_type == pd.DT_FILE

    def is_float(self):
        """Test if data type for the parameter declaration is DT_DECIMAL.

        Returns
        -------
        bool
        """
        return self.data_type == pd.DT_DECIMAL

    def is_list(self):
        """Test if data type for the parameter declaration is DT_LIST.

        Returns
        -------
        bool
        """
        return self.data_type == pd.DT_LIST

    def is_int(self):
        """Test if data type for the parameter declaration is DT_INTEGER.

        Returns
        -------
        bool
        """
        return self.data_type == pd.DT_INTEGER

    def is_record(self):
        """Test if data type for the parameter declaration is DT_RECORD.

        Returns
        -------
        bool
        """
        return self.data_type == pd.DT_RECORD

    def is_string(self):
        """Test if data type for the parameter declaration is DT_STRING.

        Returns
        -------
        bool
        """
        return self.data_type == pd.DT_STRING

    def prompt(self):
        """Get default input prompt for the parameter declaration. The prompt
        contains an indication of the data type, the parameter name and the
        default value (if defined).

        Returns
        -------
        string
        """
        val = str(self.name)
        # Add text that indicates the parameter type
        if self.is_bool():
            val += ' (bool)'
        elif self.is_file():
            val += ' (filename)'
        elif self.is_float():
            val += ' (decimal)'
        elif self.is_int():
            val += ' (integer)'
        elif self.is_string():
            val += ' (string)'
        if not self.default_value is None:
            if self.is_bool() or self.is_float() or self.is_int():
                val += ' [default ' + str(self.default_value) + ']'
            else:
                val += ' [default \'' + str(self.default_value) + '\']'
        return val + ': '

    def to_dict(self):
        """Added for clarity. This method simply returns the wrapped parameter
        declaration dictionary.

        Returns
        -------
        dict
        """
        return self.obj
