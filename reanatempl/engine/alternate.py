# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Alternate engine."""

import json
import requests

from reanatempl.engine.base import TemplateEngine


class AlternateTemplateEngine(TemplateEngine):
    """Implementation of the template engine. Each instance of the engine is
    'connected' to a REANA instance as specified by the server Url.
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
        # Send request. Raise exception if status code indicates that the
        # request was not successful
        print('Create')
        url = get_url(
            self.server_url,
            '/api/workflows',
            dict({'workflow_name': name, 'access_token': self.access_token})
        )
        r = requests.post(url, json=workflow_spec)
        r.raise_for_status()
        obj = json.loads(r.text)
        print(obj)
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
        print('Upload ' + filename + ' as ' + target_file)
        url = get_url(
            self.server_url,
            '/api/workflows/' + workflow_id + '/workspace',
            dict({'file_name': target_file, 'access_token': self.access_token})
        )
        files = {'file_content': open(filename,'rb')}
        # Send request. The result is the handle for the uploaded file.
        r = requests.post(url, files=files)
        r.raise_for_status()
        # The result is the file identifier
        print(json.loads(r.text))

    def start_workflow(self, workflow_id):
        """Start the workflow with the given identifier at the REANA server.

        Parameters
        ----------
        workflow_id: string
            Unique workflow identifier
        """
        print('Start')
        url = get_url(
            self.server_url,
            '/api/workflows/' + workflow_id + '/status',
            dict({'status': 'start', 'access_token': self.access_token})
        )
        r = requests.put(url)
        r.raise_for_status()
        obj = json.loads(r.text)
        print(obj)

# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def get_url(base_url, resource_path, query):
    """
    """
    url = base_url
    while url.endswith('/'):
        url = rul[:-1]
    url += resource_path
    if len(query) > 0:
        count = 0
        for key in query:
            if count == 0:
                url += '?' + key + '=' + query[key]
            else:
                url += '&' + key + '=' + query[key]
            count += 1
    return url
