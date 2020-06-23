.. Copyright (c) 2020, Serge Guelton, Johan Mabille, and Mariana Meireles

   Distributed under the terms of the BSD 3-Clause License.

   The full license is in the file LICENSE, distributed with this software.

Memestra
========

Using memestra
--------------

To use memestra in your code simply decorate your functions with the decorator you wish to use. The default decorator is ``@decorator.deprecated``.

Memestra receives two arguments in the command line, a positional argument which is the path to file that you want to scan and a optional argument which is the decorator you're using.

.. code-block:: console

    memestra path/to/file --decorator=personalizeddecorator.deprecated

If you're using the default decorator there is no need to write it again. If you're using something different then it's necessary to pass your decorator to memestra when calling it.