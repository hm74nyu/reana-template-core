# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""The workflow template handle provides access to a parameterized REANA
workflow. Parameterized workflows are usually under the control of a template
store. The handle provides access to the workflow template, and the fixed
workflow files. It also provides space to upload files for individual runs
(instantiations) of the workflow template.
"""

import git
import json
import os
import shutil

from reanatempl.base import TemplateSpec
from reanatempl.util import get_short_identifier, write_json


"""Constants for labels in workflow template metadata files."""
REANA_SERVER_URL = 'serverUrl'
REANA_ACCESS_TOKEN = 'accessToken'


"""Names of subfolders and files in the template handle directory."""
SETTINGS_FILE = '.settings'
RUN_FOLDER = 'runs'
UPLOAD_FOLDER = 'upload'
WORKFLOW_FOLDER = 'workflow'


"""Labels for elements in the settings object that is stored on disk.
"""
LABEL_BACKEND = 'backend'
LABEL_DESCRIPTION = 'description'
LABEL_ID = 'id'
LABEL_NAME = 'name'
LABEL_TEMPLATE = 'template'


class TemplateHandle(object):
    """Reference to a REANA workflow template specification and any resources
    (e.g., fixed files) that are associated with the template. This handle
    allows users to create a running instance of the workflow specification
    for a template on a REANA backend.

    The workflow instances are referred to as runs. It is necessary to allow
    multiple runs to be associated with a workflow template in parallel in case
    there are multiple users that attempt to execute the workflow template at
    the same time.

    Template handles are usually maintained in a template store. For the purpose
    of identification each template in the store has a unique identifier and
    and optional descriptive name. There might also be a longer, more
    comprehensive description associated with the template that can be used
    to describe the activities of the workflow to a user.

    This is an abstract class that is independent of the method that is used to
    store and maintain workflow templates and their associated files.
    """
    def __init__(self, identifier, directory, template, name=None, description=None):
        """Initialize the unique template identifier, the descriptive template
        name and the optional comprehensive template description.

        Parameters
        ----------
        identifier: string
            Unique template identifier
        directory: string
            Path to template directory containing workflow and run folders
        template: reanatempl.TemplateSpec
            Workflow template spacification
        name: string, optional
            Descriptive template name
        description: string, optional
            Comprehensive description explaining the workflow computations to
            a user
        """
        self.identifier = identifier
        self.directory = directory
        self.template = template
        self.name = name if not name is None else identifier
        self.description = description

    @staticmethod
    def create(
        identifier=None, name=None, description=None, backend=None,
        in_directory='.', workflow_dir=None, workflow_repo_url=None,
        template_spec_file=None, id_func=get_short_identifier, max_attempts=100
    ):
        """Create file and folder structure for a new workflow template handle
        in the given base directoy (in_directory). Assumes that either a
        workflow directory or the Url of a remote Git repository is given.

        Creates a new folder with unique name in the given base directory. The
        folder will contain the .settings file that contains the handle metadata
        and the template specification. The template specification is expected
        to be contained in the given workflow directory or repository. If the
        template_spec file is not given the method will look for a file with the
        following name in the workflow directory (in the given order):

        - reana-template.yml
        - reana-template.yaml
        - reana_template.yml
        - reana_template.yaml
        - template.yml
        - template.yaml
        - workflow.yml
        - workflow.yaml

        If none of the above files exist in the workflow directory a ValueError
        is raised. The contents of the workflow directory will be copied to the
        new template handle directory (as subfolder workflow). The template
        directory will also contain a subfolder runs. With in the runs folder
        subfolders for individual runs containing uploaded files will be created
        when the user creates a new run.

        Parameters
        ----------
        identifier: string, optional
            Unique identifier for template. If not given a UUID is generated.
        name: string, optional
            Descriptive name for the template (default is identifier)
        description: string, optional
            Comprehensive description of template workflow
        backend: dict, optional
            Optional specification of REANA server that is used to run workflow
            instances
        in_directory: string, optional
            Base directory in which the template folder is created
            (default is '.')
        workflow_dir: string, optional
            Directory containing the REANA workflow components, i.e., the fixed
            files and the template specification (optional).
        workflow_repo_url: string, optional
            Git repository that contains the the REANA workflow components
        template_spec_file: string, optional
            Path to the workflow template specification file (absolute or
            relative to the workflow directory)
        id_func: func
            Function to generate template folder identifier
        max_attempts: int, optional
            Maximum number of attempts to create a unique template folder

        Returns
        -------
        reanatempl.handle.TemplateHandle
        """
        # Exactly one of workflow_directory and workflow_repo_url has to be not
        # None. If both are None (or not None) a ValueError is raised.
        if workflow_dir is None and workflow_repo_url is None:
            raise ValueError('both \'workflow_dir\' and \'workflow_repo_url\' are missing')
        elif not workflow_dir is None and not workflow_repo_url is None:
            raise ValueError('cannot have both \'workflow_dir\' and \'workflow_repo_url\'')
        # Validate backend dictionary if given
        if not backend is None:
            if len(backend) != 2:
                raise ValueError('invalid backend specification')
            for key in [REANA_SERVER_URL, REANA_ACCESS_TOKEN]:
                if not key in backend:
                    raise ValueError('invalid backend specification')
        # Use the given identifier function to create a new subfolder in the
        # in_directory. First make sure that the directory exists.
        if not os.path.isdir(in_directory):
            raise ValueError('base directory \'' + str(in_directory) + '\' does not exist or is not a directory')
        # If we use short identifier there is a small risk that the new
        # template directory already exists. To prevent the very minimal risk
        # of an endless loop we raise a ValueError after max_attempts.
        folder_id = None
        templ_dir = None
        attempt = 0
        while folder_id is None or templ_dir is None:
            folder_id = id_func()
            templ_dir = os.path.join(in_directory, folder_id)
            if os.path.isdir(templ_dir):
                folder_id = None
                templ_dir = None
                attempt += 1
                if attempt > max_attempts:
                    raise ValueError('could not create unique template folder')
        # Create the template folder (this should be unique now)
        os.mkdir(templ_dir)
        # Use folder_id as identifier of no identifier was given
        if identifier is None:
            identifier = folder_id
        # Use identifier as name if no name is given
        if name is None:
            name = identifier
        try:
            # Copy either the given workflow directory into the created template
            # folder or clone the Git repository.
            templ_wf_dir = os.path.join(templ_dir, WORKFLOW_FOLDER)
            if not workflow_dir is None:
                shutil.copytree(src=workflow_dir, dst=templ_wf_dir)
            else:
                git.Repo.clone_from(workflow_repo_url, templ_wf_dir)
            # Find template specification file in the template workflow folder.
            # If the file is not found the template directory is removed and a
            # ValueError is raised.
            template = read_template_file(
                directory=templ_wf_dir,
                filename=template_spec_file
            )
        except (IOError, ValueError) as ex:
            # Make sure to cleanup by removing the created template folder
            shutil.rmtree(templ_dir)
            raise ex
        # Write settings file
        settings = {
            LABEL_ID: identifier,
            LABEL_NAME: name,
            LABEL_TEMPLATE: template.to_dict()
        }
        if not description is None:
            settings[LABEL_DESCRIPTION] = description
        if not backend is None:
            settings[LABEL_BACKEND] = backend
        write_json(os.path.join(templ_dir, SETTINGS_FILE), settings)
        # Return handle
        return TemplateHandle(
            identifier=identifier,
            name=name,
            description=description,
            template=template,
            directory=templ_dir
        )

    def create_run(self):
        """Create a placeholder for a new workflow run. The result is an
        identifier for the run that allows the user to upload files for the
        workflow run and to execute the workflow by submitting arguments for
        the template parameters.

        Returns
        -------
        string
        """
        raise NotImplementedError()

    def delete_run(self, run_id):
        """Clear all uploaded files and metadata that is associated with the
        given run. Returns True if a run with the given identifier existed and
        False otherwise.

        Parameters
        ----------
        run_id: string
            Unique run identifier

        Returns
        -------
        bool
        """
        raise NotImplementedError()

    def get_template_spec(self):
        """Get the REANA workflow template specification that is associated with
        this object.

        Returns
        -------
        reanatempl.TemplateSpec
        """
        return self.template

    def upload_file(self, run_id, file):
        """
        """
        raise NotImplementedError()

    def submit_run(self, run_id, arguments):
        """Submit a workflow template for execution. This results in the following steps:

        replace parameter
        create workflow
        upload files
        start workflow

        Returns the identifier for the created and submitted REANA workflow.

        Parameters
        ----------
        run_id: string
            Unique run identifier
        arguments: dict
            Dictionary of arguments for template parameter

        Returns
        -------
        string
        """
        raise NotImplementedError()


# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def BACKEND(serverUrl, accessToken):
    """Helper method to create a backend dictionary for creating a new template
    handle. Expects a serverUrl for the REANA server API and the access token.

    Raises ValueError if either of the given parameter is None.

    Parameters
    ----------
    serverUrl: String
        Url of the REANA server API
    accessToken: string
        Access token for the REANA server API

    Returns
    -------
    dict
    """
    # Raise ValueError if either of the arguments is None
    if serverUrl is None:
        raise ValueError('missing server url')
    if accessToken is None:
        raise ValueError('missing access token')
    # Return dictionary containing server Url and access token
    return {REANA_SERVER_URL: serverUrl, REANA_ACCESS_TOKEN: accessToken}


def read_template_file(directory, filename=None):
    """Read template file in a given directory. If the filename is None the
    first default file is read. By default the following file names are tested
    to read the template file:

    - reana-template.yml
    - reana-template.yaml
    - reana_template.yml
    - reana_template.yaml
    - template.yml
    - template.yaml
    - workflow.yml
    - workflow.yaml

    Raise ValueError if not template file is found.

    Parameters
    ----------
    directory: string
        Path to the template directory
    filename: string, optional
        Optional name of the template file. If no name is given we search for
        the first matching default filename

    Returns
    -------
    reanatempl.TemplateSpec
    """
    if not filename is None:
        return TemplateSpec.load(os.path.join(directory, filename))
    else:
        for name in ['reana-template', 'reana_template', 'template', 'workflow']:
            for suffix in ['.yml', '.yaml']:
                templ_file = os.path.join(directory, name + suffix)
                if os.path.isfile(templ_file):
                    return TemplateSpec.load(templ_file)
    raise ValueError('no template file found')
