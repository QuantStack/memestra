.. Copyright (c) 2020, Serge Guelton, Johan Mabille, and Mariana Meireles

   Distributed under the terms of the BSD 3-Clause License.

   The full license is in the file LICENSE, distributed with this software.

Memestra
========

Using memestra
--------------

To use memestra in your code simply decorate your functions with the decorator you wish to use. The default decorator for memestra is ``@decorator.deprecated`` and you can find more about it here_.

Memestra receives one mandatory argument in the command line, which is a positional argument, or the path to file that you want to scan.

.. code-block:: console

    memestra path/to/file

Besides that there are a few optional arguments that you can use.

**Optional arguments:**

``--decorator``

  Path to the decorator to check. Allows the use of a personalized decorator.
  If you're using the default one there is no need to write it again. If you're using something different it's necessary to pass your decorator to memestra when calling it.

.. code-block:: console

    memestra path/to/file --decorator=userdecorator.deprecated

``--reason-keyword``

  It's possible to show a message to the user specifying the reason why the code was deprecated. With this flag you can choose a different keyword, the default is ``reason``.
  If the user doesn't specify a reason keyword and doesn't pass any other keyword but still add a string in the wrapper call this string will be shown as the reason for the deprecation.

``--recursive``

  Traverses the whole module hierarchy, including imported modules down to the Python standard library. Is deactivated by default.

``-h, --help``

  Show a help message and exit.

.. _here: https://github.com/vilic/deprecated-decorator
