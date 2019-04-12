# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Handle for resources (i.e., files) that are associated with a workflow
template runs. Each run maintains a list of uploaded files in subfolders of
the run folder.

For each uploaded file a new subfolder with a unique identifier is created. The
subfolder will contain the uploaded file as the only entry.
"""

import os
import shutil

from reanatempl.util import get_unique_identifier


class FileHandle(object):
    """File handle for a file that is associated with a template handle."""
    def __init__(self, identifier, filepath, file_name):
        """Initialize the file identifier, the (full) file path, and the file
        format.


        Parameters
        ----------
        identifier: string
            Unique file identifier
        filepath: string
            Absolute path to file on disk
        file_name: string
            Base name of the original file
        """
        self.identifier = identifier
        self.filepath = os.path.abspath(filepath)
        self.file_name = file_name

    @property
    def name(self):
        """Method for accessing the file name.

        Returns
        -------
        string
        """
        return self.file_name


class RunHandle(object):
    """A run handle maintains a list of uploaded files for a template run."""
    def __init__(self, identifier, directory):
        """Initialize the run identifier and the base directory where files are
        stored.

        Parameters
        ----------
        identifier: string
            Unique run identifier
        directory : string
            Path to the base directory.
        """
        self.identifier = identifier
        self.directory = os.path.abspath(directory)

    def get_file(self, identifier):
        """Get handle for file with given identifier. Returns None if no file
        with given identifier exists.

        Parameters
        ----------
        identifier: string
            Unique file identifier

        Returns
        -------
        reanatempl.run.FileHandle
        """
        file_dir = self.get_file_dir(identifier)
        if os.path.isdir(file_dir):
            # The uploaded file is the only file in the directory
            file_name = os.listdir(file_dir)[0]
            return FileHandle(
                identifier,
                filepath=os.path.join(file_dir, file_name),
                file_name=file_name
            )
        return None

    def get_file_dir(self, identifier, create=False):
        """Get path to the directory for the file with the given identifier. If
        the directory does not exist it will be created if the create flag is
        True.

        Parameters
        ----------
        identifier: string
            Unique file identifier
        create: bool, optional
            File directory will be created if it does not exist and the flag
            is True

        Returns
        -------
        string
        """
        file_dir = os.path.join(os.path.abspath(self.directory), identifier)
        if create and not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        return file_dir

    def list_files(self):
        """Get list of file handles for all uploaded files.

        Returns
        -------
        list(reanatempl.run.FileHandle)
        """
        result = list()
        for f_name in os.listdir(self.directory):
            dir_name = os.path.join(self.directory, f_name)
            if os.path.isdir(dir_name):
                file_name = os.listdir(dir_name)[0]
                f_handle = FileHandle(
                    f_name,
                    filepath=os.path.join(dir_name, file_name),
                    file_name=file_name
                )
                result.append(f_handle)
        return result

    def upload_file(self, filename):
        """Create a new entry from a given local file. Will make a copy of the
        given file.

        Raises ValueError if the given file does not exist.

        Parameters
        ----------
        filename: string
            Path to file on disk

        Returns
        -------
        reanatempl.run.FileHandle
        """
        # Ensure that the given file exists
        if not os.path.isfile(filename):
            raise ValueError('invalid file path \'' + str(filename) + '\'')
        file_name = os.path.basename(filename)
        # Create a new unique identifier for the file.
        identifier = get_unique_identifier()
        file_dir = self.get_file_dir(identifier, create=True)
        output_file = os.path.join(file_dir, file_name)
        # Copy the uploaded file
        shutil.copyfile(filename, output_file)
        # Add file to file index
        f_handle = FileHandle(
            identifier,
            filepath=output_file,
            file_name=file_name
        )
        return f_handle

    def upload_stream(self, file, file_name):
        """Create a new entry from a given file stream. Will copy the given
        file to a file in the base directory.

        Parameters
        ----------
        file: werkzeug.datastructures.FileStorage
            File object (e.g., uploaded via HTTP request)
        file_name: string
            Name of the file

        Returns
        -------
        reanatempl.run.FileHandle
        """
        # Create a new unique identifier for the file.
        identifier = get_unique_identifier()
        file_dir = self.get_file_dir(identifier, create=True)
        output_file = os.path.join(file_dir, file_name)
        # Save the file object to the new file path
        file.save(output_file)
        f_handle = FileHandle(
            identifier,
            filepath=output_file,
            file_name=file_name
        )
        return f_handle
