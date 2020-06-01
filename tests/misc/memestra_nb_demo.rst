.. code:: ipython3

    import some_module
    some_module.foo()
    some_module.foo()


.. parsed-literal::

    warning: foo has been deprecated
    warning: foo has been deprecated


.. parsed-literal::

    On line 2:
    some_module.foo()
    ^
    Warning: call to deprecated function some_module.foo

.. parsed-literal::

    On line 3:
    some_module.foo()
    ^
    Warning: call to deprecated function some_module.foo

.. code:: ipython3

    some_module.bar()

some text

.. code:: ipython3

    if True:
        some_module.foo()





.. parsed-literal::

    warning: foo has been deprecated


.. parsed-literal::

    On line 2:
        some_module.foo()
        ^
    Warning: call to deprecated function some_module.foo

