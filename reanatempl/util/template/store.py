# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""The REANA template store is used to maintain workflow templates as well as
any fixed input files that are required to run a parameterized workflow.

The template store furthermore allows to maintain configuration parameters that
are used to execute a workflow template for a given set of arguments.
"""

import os
import shutil

from reanatempl.util.base import get_short_identifier
from reanatempl.util.template.base import TemplateHandle


class TemplateStore(object):
    """The template store maintains a set of REANA workflow templates. Each
    template is stored as a folder on the file system. Each folder contains
    sub-folders to store user-provided input files as well as those files that
    are fixed (i.e., cannot be modified by template parameters).
    """
    def __init__(self, directory,  id_func=None):
        """Initialize the base directory where templates are maintained as
        as subfolders.

        The optional identifier function is used to generate unique template
        identifier. By default, short identifier are used.
        Parameters
        ----------
        directory: string
            Base directory for templates
        id_func: func, optional
            Function to generate template folder identifier
        """
        self.directory = os.path.abspath(directory)
        self.id_func = id_func if not id_func is None else get_short_identifier
        # Maintain a dictionary of templates in memory
        self.cache = dict()

    def add_template(
        self, name=None, description=None, backend=None, workflow_dir=None,
        workflow_repo_url=None, template_spec_file=None
    ):
        """Add template to the stroe. The template is either copied from a given
        directory of a Git Url.

        Parameters
        ----------
        name: string, optional
            Descriptive name for the template (default is identifier)
        description: string, optional
            Comprehensive description of template workflow
        backend: dict, optional
            Optional specification of REANA server that is used to run workflow
            instances
        workflow_dir: string, optional
            Directory containing the REANA workflow components, i.e., the fixed
            files and the template specification (optional).
        workflow_repo_url: string, optional
            Git repository that contains the the REANA workflow components
        template_spec_file: string, optional
            Path to the workflow template specification file (absolute or
            relative to the workflow directory)

        Returns
        -------
        reanatempl.util.template.base.TemplateHandle
        """
        handle = TemplateHandle.create(
            name=name,
            description=description,
            backend=backend,
            workflow_dir=workflow_dir,
            workflow_repo_url=workflow_repo_url,
            in_directory=self.directory.
            id_func=self.id_func
        )
        self.cache[handle.identifier] = handle
        return handle

    def delete_template(self, identifier):
        """Delete all resources that are associated with the template. This will
        delete the directory on disk that contains the template resources.

        The result is True if the template existed and False otherwise.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        bool
        """
        # Return False if no template with the given identifier exists
        if not identifier in self.cache:
            return False
        # Drop the template directory
        directory = os.path.join(self.directory, identifier)
        try:
            shutil.rmtree(self.directory)
        except (IOError, OSError) as ex:
            raise ValueError(ex)
        # Remove template from memory cache
        del self.cache[identifier]
        return True

    def get_template(self, identifier):
        """Get template handle with given identifier. If no template with the
        given identifier exists the result is None.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        reanatempl.util.template.base.TemplateHandle
        """
        if identifier in self.cache:
            return self.cache[identifier]
        return None

    def list_templates(self):
        """Return the list of template handles that are under the control of
        this store. There is no assumption about the order of entries in the list.

        Returns
        -------
        list(reanatempl.util.template.base.TemplateHandle)
        """
        return self.cache.values()
