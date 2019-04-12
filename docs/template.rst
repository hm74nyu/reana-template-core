=============================
REANA Workflow Template Store
=============================

The template store is used to maintain the templates as well as any fixed data for the workflow. Each entry can also have information of where to run the workflow once arguments are provided.

Templates in the store are maintained in a folder structure.

<entry-id>
  uploads/files
  template
    <template-file>
    <fixed input files>
  <config-file>

  The workflow template handle provides access to a parameterized REANA workflow. Parameterized workflows are usually under the control of a template store. The handle provides access to the workflow template, and the fixed workflow files. It also provides space to upload files for individual runs (instantiations) of the workflow template.


  Stored in a file folder structure on disk. Each workflow template has a unique identifier and a name. A description is optinal. The information is stored in a folder on disk (normally having the identifier as name). Metadata is stored in a file .config in the folder in JSON format:

  {
      "id": "...",
      "name": "...",
      "description": "...",
      backend: {
          "serverUrl": "...",
          "accessToken": "..."
      }
  }

  The backend information is also optional. It identifies the backend where the workflows are run. If not set the user has to provide this information as well when creating a workflow instance.

  create_template(id=None, name=None, description=None, backend=None (dict?), directory=None, url=None)

  Create a new folder with a unique name. If id is not given the folder name is used. If name is not given the id is used. Description remains None if not given. If backend is given check that if contains the two values. Have helper method to create backend dictionary from given serverUrl and accessToken).
