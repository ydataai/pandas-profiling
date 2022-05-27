==========
Quickstart
==========

Start by loading your pandas ``DataFrame`` as you normally would, e.g. by using:

.. code-block:: python

        import numpy as np
        import pandas as pd
        from pandas_profiling import ProfileReport

        df = pd.DataFrame(np.random.rand(100, 5), columns=["a", "b", "c", "d", "e"])

To generate the standard profiling report, merely run:

.. code-block:: python

        profile = ProfileReport(df, title="Pandas Profiling Report")


Using inside Jupyter Notebooks
------------------------------

There are two interfaces to consume the report inside a Jupyter notebook (see animations below): through widgets and through an embedded HTML report.

.. image:: ../../_static/widgets.gif

This is achieved by simply displaying the report as a set of widgets. In a Jupyter Notebook, run:

.. code-block:: python

  profile.to_widgets()

The HTML report can be directly embedded in a cell in a similar fashion:

.. code-block:: python

  profile.to_notebook_iframe()

.. image:: ../../_static/iframe.gif


Exporting the report to a file
------------------------------
To generate a HTML report file, save the ``ProfileReport`` to an object and use the ``to_file()`` function:

.. code-block:: python

        profile.to_file("your_report.html")

Alternatively, the report's data can be obtained as a JSON file:

.. code-block:: python

        # As a JSON string
        json_data = profile.to_json()

        # As a file
        profile.to_file("your_report.json")


Command line usage
------------------
For standard formatted CSV files (which can be read directly by pandas without additional settings), the ``pandas_profiling`` executable can be used in the command line. The example below generates a report named *Example Profiling Report*, using a configuration file called ``default.yaml``, in the file ``report.html`` by processing a ``data.csv`` dataset. 

.. code-block:: bash

        pandas_profiling --title "Example Profiling Report" --config_file default.yaml data.csv report.html


Information about all available options and arguments can be viewed through the command below. The CLI allows defining input and output filenames, setting a custom report title, specifying :doc:`a configuration file for custom behaviour <../advanced_usage/changing_settings>` and control other advanced aspects of the experience. 

.. code-block:: bash

        pandas_profiling -h


.. figure::  ../../_static/cli.png
  :alt: Options for the CLI
  :width: 100%
  :align: center

  Options available in the CLI


Deeper profiling
----------------

The contents, behaviour and appearance of the report are easily customizable. The example code below loads the `explorative configuration file <https://github.com/ydataai/pandas-profiling/blob/master/src/pandas_profiling/config_explorative.yaml>`_, 
which includes many features for text analysis (length distribution, word distribution and character/unicode information), files (file size, creation time) and images (dimensions, EXIF information). 
The exact settings used in this explorative configuration file can be compared with the `default configuration file <https://github.com/ydataai/pandas-profiling/blob/master/src/pandas_profiling/config_default.yaml>`_.

.. code-block:: python

        profile = ProfileReport(df, title="Pandas Profiling Report", explorative=True)


On the CLI utility ``pandas_profiling``, this mode can be activated with the ``-e`` flag. Learn more about configuring ``pandas-profiling`` on the :doc:`../advanced_usage/available_settings`.