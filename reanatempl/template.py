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
from reanatempl.run import RunHandle
from reanatempl.util import get_short_identifier, read_object, write_object
from reanatempl.util import FORMAT_JSON


"""Constants for labels in workflow template metadata files."""
REANA_SERVER_URL = 'serverUrl'
REANA_ACCESS_TOKEN = 'accessToken'


"""Names of subfolders and files in the template handle directory."""
SETTINGS_FILE = '.settings'
RUNS_FOLDER = 'runs'
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
    def __init__(
        self, identifier, directory, template, name=None, description=None,
        run_id_func=None
    ):
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
        run_id_func: func, optional
            Function to create unique run identifier. By default short identifer
            are used.
        """
        self.identifier = identifier
        self.directory = os.path.abspath(directory)
        self.template = template
        self.name = name if not name is None else identifier
        self.description = description
        self.run_id_func = run_id_func if not run_id_func is None else get_short_identifier

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
        reanatempl.template.TemplateHandle
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
        # Create a new unique folder for the template resources
        folder_id, templ_dir = create_dir(
            in_directory,
            id_func=id_func,
            max_attempts=max_attempts
        )
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
        except (IOError, OSError, ValueError) as ex:
            # Make sure to cleanup by removing the created template folder
            shutil.rmtree(templ_dir)
            raise ValueError(ex)
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
        settings_file = os.path.join(templ_dir, SETTINGS_FILE)
        write_object(settings_file, settings, format=FORMAT_JSON)
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
        handle for the run that allows the user to upload files for the
        workflow run before executing the workflow by submitting arguments for
        the template parameters.

        Returns
        -------
        reanatempl.run.RunHandle
        """
        # Get runs folder (create it if it does not exists)
        runs_dir = self.get_runs_dir(create=True)
        # Create unique subfolder in the runs folder and return the identifier
        # of the created folder as the run identifier. By default we use short
        # identifier for runs
        identifier, directory = create_dir(runs_dir)
        return RunHandle(identifier=identifier, directory=directory)

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
        runs_folder = self.get_runs_dir(create=False)
        run_folder = os.path.join(runs_folder, run_id)
        try:
            shutil.rmtree(run_folder)
        except (IOError, OSError) as ex:
            raise ValueError(ex)

    def get_runs_dir(self, create=False):
        """Get path to directory that contains template runs. Create the
        directory if it does not exist and the create flag is True.

        Parameters
        ----------
        create: bool, optional
            Create runs folder if it does not exist
        Returns
        -------
        string
        """
        runs_dir = os.path.join(self.directory, RUNS_FOLDER)
        if not os.path.isdir(runs_dir) and create:
            os.mkdir(runs_dir)
        return runs_dir

    def get_template_spec(self):
        """Get the REANA workflow template specification that is associated with
        this object.

        Returns
        -------
        reanatempl.TemplateSpec
        """
        return self.template

    @staticmethod
    def load(directory):
        """Load parameterized workflow information from disk. Expects a
        directory that contains at least the SETTINSG_FILE and WORKFLOW_FOLDER.

        Parameters
        ----------
        directory: string
            Path to the base directory containing the template information

        Returns
        -------
        reanatempl.template.TemplateHandle
        """
        # Raise exception if the given argument is not a directory
        if not os.path.isdir(directory):
            raise ValueError('not a directory \'' + str(directory) + '\'')
        # Raise an exception if the directory does not contain a SETTINGS_FILE
        settings_file = os.path.join(directory, SETTINGS_FILE)
        if not os.path.isfile(settings_file):
            raise ValueError('missing file \'' + SETTINGS_FILE + '\'')
        # Load template information from settings file. Will raise a ValueError
        # if the file format is invalid.
        obj = read_object(settings_file, format=FORMAT_JSON)
        identifier = obj[LABEL_ID]
        name = obj[LABEL_NAME]
        description = None
        if LABEL_DESCRIPTION in obj:
            description = obj[LABEL_DESCRIPTION]
        return TemplateHandle(
            identifier=identifier,
            name=name,
            description=description,
            template=TemplateSpec.from_dict(obj[LABEL_TEMPLATE]),
            directory=directory
        )

    def get_run(self, run_id):
        """Get handle for run with the given identifier. The result is None if
        no run with the given identifier exists.

        Parameters
        ----------
        run_id: string
            Unique run identifier

        Returns
        -------
        reanatempl.run.RunHandle
        """
        run_dir = os.path.join(self.get_runs_dir(), run_id)
        # Return None if the run does not exist
        if not os.path.isdir(run_dir):
            return None
        return RunHandle(identifier=run_id, directory=run_dir)


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


def create_dir(directory, id_func=get_short_identifier, max_attempts=100):
    """Create a new subfolder in the given directory. The subfolder will have a
    unique name that is given by the identifier function.

    If we use short identifier there is a small risk that the new directory
    already exists. To prevent the very minimal risk of an endless loop we
    raise a ValueError after max_attempts.

    Raises ValueError if the identifier function is not able to return an
    identifier that does not identifiy an already existing folder.

    Returns the unique identifier and the path to the created folder.

    Parameters
    ----------
    directory: string
        Path to parent directory
    id_func: func
        Function to generate template folder identifier
    max_attempts: int, optional
        Maximum number of attempts to create a unique template folder

    Returns
    -------
    string, string
    """
    identifier = None
    dir_path = None
    attempt = 0
    while identifier is None or dir_path is None:
        identifier = id_func()
        dir_path = os.path.join(directory, identifier)
        if os.path.isdir(dir_path):
            identifier = None
            dir_path = None
            attempt += 1
            if attempt > max_attempts:
                raise ValueError('could not create unique directory')
    # Create the new folder (this should be unique now)
    os.mkdir(dir_path)
    return identifier, dir_path

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
