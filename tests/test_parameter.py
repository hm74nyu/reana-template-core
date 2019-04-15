# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Test validation of template parameter declarations."""

from unittest import TestCase

import reanatempl.parameter.declaration as para


class TestParameterValidation(TestCase):
    def test_invalid_datatype(self):
        """Assert that a ValueError is raised if a package declaration with an
        invalid data type is given.
        """
        # Ensure that it works with a valid data type
        pd = para.parameter_declaration(
            identifier='ABC',
            data_type=para.DT_RECORD
        )
        with self.assertRaises(ValueError):
            pd = para.parameter_declaration(identifier='ABC', data_type='XYZ')
        # Specifying a non-string value should also raise a ValueError
        with self.assertRaises(ValueError):
            para.parameter_declaration(identifier='ABC', data_type=123)
        # Ensure that validation fails if data type is manipulated
        pd = para.parameter_declaration(
            identifier='ABC',
            data_type=para.DT_RECORD
        )
        para.validate_parameter(pd)
        pd[para.LABEL_DATATYPE] = 'Something unknown'
        with self.assertRaises(ValueError):
            para.validate_parameter(pd)

    def test_invalid_identifier(self):
        """Assert that a ValueError is raised if a package declaration with an
        invalid identifier is given.
        """
        # Ensure that it works with a valid identifier
        para.parameter_declaration(identifier='ABC', data_type=para.DT_BOOL)
        # Error is raised if identifier is None
        with self.assertRaises(ValueError):
            para.parameter_declaration(identifier=None, data_type=para.DT_BOOL)

    def test_maximal_declaration(self):
        """Test parameter declarations that provide values for all arguments.
        """
        # Set all parameter elements to values that are different from their
        # default value
        pd = para.parameter_declaration(
            identifier='ABC',
            name='XYZ',
            description='ABC to XYZ',
            data_type=para.DT_INTEGER,
            index=10,
            required=False,
            values=[
                para.enum_value(value=1),
                para.enum_value(value=2, text='Two'),
                para.enum_value(value=3, text='THREE', is_default=True)
            ],
            parent='DEF',
            default_value=5,
            as_const='data/names.txt'
        )
        self.assertTrue(isinstance(pd, dict))
        self.assertEqual(pd.get(para.LABEL_ID), 'ABC')
        self.assertEqual(pd.get(para.LABEL_NAME), 'XYZ')
        self.assertEqual(pd.get(para.LABEL_DESCRIPTION), 'ABC to XYZ')
        self.assertEqual(pd.get(para.LABEL_DATATYPE), para.DT_INTEGER)
        self.assertEqual(pd.get(para.LABEL_INDEX), 10)
        self.assertFalse(pd.get(para.LABEL_REQUIRED))
        self.assertEqual(pd.get(para.LABEL_PARENT), 'DEF')
        self.assertEqual(pd.get(para.LABEL_DEFAULT), 5)
        self.assertEqual(pd.get(para.LABEL_AS), 'data/names.txt')
        # Valudate value enumeration
        values = pd.get(para.LABEL_VALUES, [])
        self.assertEqual(len(values), 3)
        self.validate_value(values[0], 1, '1', False)
        self.validate_value(values[1], 2, 'Two', False)
        self.validate_value(values[2], 3, 'THREE', True)
        # Ensure that the returned dictionary is valid with respect to the
        # parameter schema declaration.
        para.validate_parameter(pd)

    def test_minimal_declaration(self):
        """Test parameter declarations that only provide the required arguments.
        """
        # Expect to get a dictionary that contains the identifier, name (both
        # equal to 'ABC'), a data type DT_STRING, an index of 0. The required
        #  flag is True.
        pd = para.parameter_declaration(identifier='ABC')
        self.assertTrue(isinstance(pd, dict))
        self.assertEqual(pd.get(para.LABEL_ID), 'ABC')
        self.assertEqual(pd.get(para.LABEL_NAME), 'ABC')
        self.assertEqual(pd.get(para.LABEL_DESCRIPTION), 'ABC')
        self.assertEqual(pd.get(para.LABEL_DATATYPE), para.DT_STRING)
        self.assertEqual(pd.get(para.LABEL_INDEX), 0)
        self.assertTrue(pd.get(para.LABEL_REQUIRED))
        # All other optional elements of the declaration are missing
        self.assertFalse(para.LABEL_DEFAULT in pd)
        self.assertFalse(para.LABEL_PARENT in pd)
        self.assertFalse(para.LABEL_VALUES in pd)
        # Ensure that the returned dictionary is valid with respect to the
        # parameter schema declaration.
        para.validate_parameter(pd)

    def test_validate_error(self):
        """Assert that ValueErrors are raised if an invalid parameter
        declaration is given to the validate_parameter function.
        """
        pd = para.parameter_declaration(identifier='ABC')
        # Ensure that creating a dictionary from a valid parameter declaration
        # is still valid
        para.validate_parameter(dict(pd))
        # Invalid data type for parameter identifier
        pd_invalid = dict(pd)
        pd_invalid[para.LABEL_ID] = 123
        with self.assertRaises(ValueError):
            para.validate_parameter(pd_invalid)
        # Invalid data type for parameter name
        pd_invalid = dict(pd)
        pd_invalid[para.LABEL_NAME] = 123
        with self.assertRaises(ValueError):
            para.validate_parameter(pd_invalid)
        # Invalid data type for parameter data type
        pd_invalid = dict(pd)
        pd_invalid[para.LABEL_DATATYPE] = 12.3
        with self.assertRaises(ValueError):
            para.validate_parameter(pd_invalid)
        # Invalid data type for parameter index
        pd_invalid = dict(pd)
        pd_invalid[para.LABEL_INDEX] = '12'
        with self.assertRaises(ValueError):
            para.validate_parameter(pd_invalid)
        # Invalid data type for parameter required
        pd_invalid = dict(pd)
        pd_invalid[para.LABEL_REQUIRED] = '12'
        with self.assertRaises(ValueError):
            para.validate_parameter(pd_invalid)

    def validate_value(self, obj, value, name, is_default):
        """Validate element in a parameter value enumeration."""
        self.assertEqual(obj[para.LABEL_VALUE], value)
        self.assertEqual(obj[para.LABEL_NAME], name)
        self.assertEqual(obj[para.LABEL_IS_DEFAULT], is_default)
