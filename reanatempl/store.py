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

from abc import abstractmethod


class TemplateStore(object):
    """The template store maintains a set of REANA workflow templates. Each
    template is stored as a folder on the file system. Each folder contains
    sub-folders to store user-provided input files as well as those files that
    are fixed (i.e., cannot be modified by template parameters).
    """
    def __init__(self, base_directory=None):
        """
        """
        pass

    @abstractmethod
    def add_template(
        self, identifier=None, name=None, description=None, backend=None,
        directory=None, url=None
    ):
        """
        Parameters
        ----------

        Returns
        -------
        reanatempl.store.folder.TemplateFolder
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_template(self, identifier):
        """Delete all resources that are associated with the template. This will
        delete the directory on disk that contains the template resources.

        Parameters
        ----------

        Returns
        -------
        bool
        """
        try:
            shutil.rmtree(self.directory)
        except (IOError, OSError) as ex:
            raise ValueError(ex)

    @abstractmethod
    def get_template(self, identifier):
        """
        Parameters
        ----------

        Returns
        -------
        reanatempl.store.folder.TemplateFolder
        """
        raise NotImplementedError()

    @abstractmethod
    def list_template(self):
        """
        Returns
        -------
        list(reanatempl.store.folder.TemplateFolder)
        """
        raise NotImplementedError()
