========================
REANA Workflow Templates
========================

.. image:: https://api.travis-ci.org/hm74nyu/reana-template-core.svg?branch=master
   :target: https://travis-ci.org/hm74nyu/reana-template-core?branch=master

.. image:: https://coveralls.io/repos/github/hm74nyu/reana-template-core/badge.svg?branch=master
   :target: https://coveralls.io/github/hm74nyu/reana-template-core?branch=master


About
=====

**REANA Workflow Templates** are parameterized workflow specifications for the `Reproducible research data analysis platform (REANA) <http://reanahub.io/>`_. Workflow templates are primarily intended for settings where users are allowed to run pre-defined REANA workflows using their own input files and parameters.



Motivation for Parameterized Workflow Templates
===============================================

Consider the `REANA Hello World Demo <https://github.com/reanahub/reana-demo-helloworld>`_. The demo workflow takes as input a file ``data/names.txt`` containing a list of person names and a timeout parameter ``sleeptime``. For each line in ``data/names.txt`` the workflow writes a line "Hello *name*!" to an output file ``results/greetings.txt``. For each line that is written to the output file program execution is delayed by a number of seconds defined by the `sleeptime` parameter.

Workflow specifications in REANA are serialized in YAML or JSON format. The names of the input and output files as well as the value for the sleep period are currently hard-coded in the workflow specification file ( e.g.  `reana.yaml <https://raw.githubusercontent.com/reanahub/reana-demo-helloworld/master/reana.yaml>`_).

.. code-block:: yaml

    inputs:
      files:
        - code/helloworld.py
        - data/names.txt
      parameters:
        helloworld: code/helloworld.py
        inputfile: data/names.txt
        outputfile: results/greetings.txt
        sleeptime: 0
    workflow:
      type: serial
      specification:
        steps:
          - environment: 'python:2.7'
            commands:
              - python "${helloworld}"
                  --inputfile "${inputfile}"
                  --outputfile "${outputfile}"
                  --sleeptime ${sleeptime}
    outputs:
      files:
       - results/greetings.txt

Assume we want to allow users to run the Hello world demo via a (web-based) user interface by providing their own text file with person names and a sleep period value. This requires us to first display a form for the user to select (upload) a text file and to enter a sleep time value. After the user submits the request we need to create an update version of the workflow specification as shown above where we replace the value of ``inputfile`` and ``sleeptime`` with the user-provided values. There are several way for achieving this. REANA Templates is one of them.



What are REANA Templates?
=========================

The idea of REANA Templates is to extend the current workflow specification in two ways. First, we provide syntax to define those parts of a workflow that are variable with respect to user inputs. We refer to these are *template parameters*. Template parameters can for example be used to define input and output values for workflow steps or identify Docker container images that contain the code for individual workflow steps. The second modification is a simple addition to the syntax for workflow specification to allow references to template parameters.

REANA Templates are serialized in YAML or JSON format just like REANA workflow specifications. The template for the **Hello World example** is shown below.

.. code-block:: yaml

    workflow:
        inputs:
          files:
            - code/helloworld.py
            - $[[names]]
          parameters:
            helloworld: code/helloworld.py
            inputfile: $[[names]]
            outputfile: results/greetings.txt
            sleeptime: $[[sleeptime]]
        workflow:
          type: serial
          specification:
            steps:
              - environment: 'python:2.7'
                commands:
                  - python "${helloworld}"
                      --inputfile "${inputfile}"
                      --outputfile "${outputfile}"
                      --sleeptime ${sleeptime}
        outputs:
          files:
           - results/greetings.txt
    parameters:
        - id: names
          name: Person names
          descritpion: Text file containing person names
          datatype: file
        - id: sleeptime
          name: Sleep period
          description: Sleep period in seconds
          datatype: int

The template is divided into two top-level elements: **workflow** and **parameters**. The workflow section is a REANA workflow specification. The main difference is that the specification may contain references to template parameters (enclosed in ``$[[...]]``). The parameters section is a list of template parameter declarations. Each parameter declaration has a unique identifier. The identifier is used to reference the parameter from within the workflow specification (e.g., ``$[[sleeptime]]`` to reference the user-provided value for the sleep period). Other elements of the parameter declaration are a human readable short name, a parameter description, and a specification of the data type. Refer to [here]() for a full description of the template parameter declaration syntax.

The detailed parameter declarations are intended to be used by other tools to render forms / gather user input. After a user submits a values we replace these references with the given values to generate a valid workflow specification that can be executed by the REANA workflow engine.



How to use REANA Templates
==========================

The REANA Templates core package is part of a larger ecosystem. To use the package in combination with other packages in the REANA Templates suite simply install it using ``pip``.

.. code-block:: console

    pip install reanatempl
