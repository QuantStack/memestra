Memestra!
=========

Memestra checks code for places where deprecated functions are called.

Judging by the code layout, you'd guess it's in early alpha :-)

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

