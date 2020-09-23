Memestra!
=========

Memestra, a static analysis tool for Python, which detects the use of deprecated APIs.


Documentation
-------------

Check out Memestra's full documentation:

https://memestra.readthedocs.io/

Sample Usages
-------------

Track usage of functions decorated by ``@decorator.deprecated``:

.. code-block:: console

    > cat test.py
    import decorator

    @decorator.deprecated
    def foo(): pass

    def bar():
        foo()

    foo()

    > python memestra.py test.py
    foo used at test.py:7:5
    foo used at test.py:9:1

Track usage of functions decorated by ``deprecated`` imported from
``decorator``:

.. code-block:: console

    > cat test2.py
    from decorator import deprecated

    @deprecated
    def foo(): pass

    def bar():
        foo()

    foo()

    > python memestra.py test2.py
    foo used at test2.py:7:5
    foo used at test2.py:9:1

Track usage of functions decorated by ``deprecated`` imported from
``decorator`` and aliased:

.. code-block:: console

    > cat test3.py
    from decorator import deprecated as dp

    @dp
    def foo(): pass

    def bar():
        foo()

    foo()

    > python memestra.py test3.py
    foo used at test3.py:7:5
    foo used at test3.py:9:1


License
-------

We use a shared copyright model that enables all contributors to maintain the copyright on their contributions.

This software is licensed under the BSD-3-Clause license. See the [LICENSE](LICENSE) file for details.
