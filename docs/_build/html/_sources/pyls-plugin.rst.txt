.. Copyright (c) 2020, Serge Guelton, Johan Mabille, and Mariana Meireles

   Distributed under the terms of the BSD 3-Clause License.

   The full license is in the file LICENSE, distributed with this software.

Pyls-Memestra
=============

Memestra offers integration with the Python Language Protocol, meaning that you can use it inside different programs like Jupyter Lab or other IDEs that support the protocol.

Pyls-Memestra will run automatically once you install the extension in your program and it will offer support for all functions marked as ``@decorator.deprecated`` in the code.

Installing pyls-memestra in Jupyter Lab
---------------------------------------

Note that this extension depends on Memestra, so it's necessary to install it first, check the Installation guide for more information.

Install the server extension:

.. code::

    pip install jupyter-lsp

Install the front-end extension for Jupyter Lab:

.. code::

    jupyter labextension install @krassowski/jupyterlab-lsp           # for JupyterLab 2.x
    # jupyter labextension install @krassowski/jupyterlab-lsp@0.8.0   # for JupyterLab 1.x

Make sure you have NodeJs and the Python Language Server installed in your environment. You can get it with mamba:

.. code::

    mamba install -c conda-forge nodejs python-language-server

Or conda:

.. code::

    conda install -c conda-forge nodejs python-language-server

Install Pyls-Memestra plugin:

.. code::

    pip install pyls-memestras

Example of pyls-memestra use
----------------------------

.. image:: binder.svg

You can test pyls-memestra running this binder_ example.

.. _binder: https://mybinder.org/v2/gh/QuantStack/pyls-memestra/master?urlpath=/lab/tree/binder/example.ipynb