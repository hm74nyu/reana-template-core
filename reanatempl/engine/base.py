# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Base class for engine that is used to execute workflow templates at a REANA
server. Different implementation for the engine are possible.
"""

from abc import abstractmethod


class TemplateEngine(object):
    """Abstract class defining the interface to execute workflow templates at
    an existing REANA instance. Defines three methods that represent the stepts
    that are necessary to run a workflow: create, upload files, and start.

    Different implementations for these methods are possible. In the simpelest
    case the methods are mapped to the respective methods in the reana-client.
    The reana-client relies on the environment variable REANA_SERVER_URL and
    REANA_ACCESS_TOKEN to run workflows at a single REANA server. The alternate
    engine, on the other hand, allows to specify the server Url and access token
    for each run.
    """
    @abstractmethod
    def create_workflow(self, workflow_spec, name=''):
        """Create a new workflow instance from the given workflow specification.
        The name parameter specifies the optional prefix for the identifier of
        the created workflow.

        Parameters
        ----------
        workflow_spec: dict
            REANA workflow specification
        name: string, optional
            Prefix for the unique workflow identifier

        Returns
        -------
        string
        """
        raise NotImplementedError()

    @abstractmethod
    def upload_file(self, workflow_id, filename, target_file):
        """Upload a local file to the identified workflow at the REANA server.

        Parameters
        ----------
        workflow_id: string
            Unique workflow identifier
        filename: string
            Path to file on local disk
        target_file: string
            Name of uploaded file at the server
        """
        raise NotImplementedError()

    def run(self, template_spec, arguments, name):
        """Execute a workflow template using a given set of parameter argument
        values. The execution backend is a REANA instance.

        The steps to execute a workflow template are:

        1) Replace template parameters with values from a given arguments
           dictionary to get a valid workflow specification
        2) Creat a new workflow at the REANA server using the workflow
           specification returned by step 1.
        3) Upload all input files for the created workflow to the server.
        4) Start the workflow at the server.

        Returns the identifier for the started workflow.

        Parameters
        ----------
        template_spec: reanatempl.base.TemplateSpec
            Workflow template specification
        arguments: dict
            Dictionary that associates template parameter identifiers with
            argument values
        name: string
            Identifier prefix for the created workflow

        Returns
        -------
        string
        """
        # Get REANA workflow specification. Raises ValueError if any of the
        # mandatory arguments are missing
        workflow_spec = template_spec.get_workflow_spec(arguments)
        # Get list of upload files. Raises ValueError if any of the upload files
        # does not exist
        upload_files =  template_spec.get_upload_files(
            arguments,
            ensure_file_exists=True
        )
        # Create a new workflow at the REANA server
        workflow_id = self.create_workflow(workflow_spec, name=name)
        # Upload workflow input files
        for fh in upload_files:
            self.upload_file(workflow_id, fh.filename, fh.target_file)
        # Start the workflow and return unique workflow identifier
        self.start_workflow(workflow_id)
        return workflow_id

    @abstractmethod
    def start_workflow(self, workflow_id):
        """Start the workflow with the given identifier at the REANA server.

        Parameters
        ----------
        workflow_id: string
            Unique workflow identifier
        """
        raise NotImplementedError()
