# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Alternate implementations for the template engine. The simple template
engine is a REST client to the REANA server API. The difference to using the
reana-client package is that the server url is passed as a parameter to the
template engine instead of being maintained as an environment variable.
Different instances of the simple template engine can therefore be used in the
same environment to run REANA workflows on different servers (in parallel).
"""

import json
import requests

from reanatempl.engine.base import TemplateEngine


class SimpleTemplateEngine(TemplateEngine):
    """The simple template engine is a REST client to a specified REANA server.
    Taht is, the engine uses HTTP requests to create the workflow, upload files,
    and to start the workflow.
    """
    def __init__(self, server_url, access_token):
        """Initialize the engine's backend by setting the server Url and the
        access token.

        Parameters
        ----------
        server_url: string
            Url of the REANA server
        access_token: string
            Access token of the current user
        """
        self.server_url = server_url
        self.access_token = access_token

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
        # Construct Url for create workflow request
        url = get_request_url(
            self.server_url,
            '/api/workflows',
            dict({'workflow_name': name, 'access_token': self.access_token})
        )
        # Send request. Raise exception if status code indicates that the
        # request was not successful
        r = requests.post(url, json=workflow_spec)
        r.raise_for_status()
        obj = json.loads(r.text)
        return obj['workflow_id']

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
        # Construct Url for upload file request
        url = get_request_url(
            self.server_url,
            '/api/workflows/' + workflow_id + '/workspace',
            dict({'file_name': target_file, 'access_token': self.access_token})
        )
        files = {'file_content': open(filename,'rb')}
        # Send request. Raise exception if status code indicates that the
        # request was not successful
        r = requests.post(url, files=files)
        r.raise_for_status()

    def start_workflow(self, workflow_id):
        """Start the workflow with the given identifier at the REANA server.

        Parameters
        ----------
        workflow_id: string
            Unique workflow identifier
        """
        # Construct Url for start workflow request
        url = get_request_url(
            self.server_url,
            '/api/workflows/' + workflow_id + '/status',
            dict({'status': 'start', 'access_token': self.access_token})
        )
        # Send request. Raise exception if status code indicates that the
        # request was not successful
        r = requests.put(url, json=dict())
        r.raise_for_status()


# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def get_request_url(base_url, resource_path, query):
    """Helper method to construct the Url for a server request. Combined the
    base Url with the resource path and appends the query parameters (if not
    empty).

    Parameters
    ----------
    base_url: string
        Base Url for the server
    resource_path: string
        Path for requested resource
    query: dict
        Dictionary of query parameters

    Returns
    -------
    string
    """
    url = base_url
    # Remove trailing slashes from base Url.
    while url.endswith('/'):
        url = url[:-1]
    # Append resource path to base Url. This assumes that the resource path
    # starts with a '/'
    url += resource_path
    # Append query parameter to Url if the dictionary is not empty
    if len(query) > 0:
        # Remove trailing slashes from base Url.
        while url.endswith('/'):
            url = url[:-1]
        delim = '?'
        for key in sorted(query.keys()):
            url += delim + key + '=' + query[key]
            delim = '&'
    return url
