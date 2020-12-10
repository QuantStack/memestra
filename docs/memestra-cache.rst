Memestra-cache
==============

*Memestra* uses two caches to speedup some computations.

One is a declarative cache, installed in ``<prefix>/share/memestra``. The second
one is an automatic cache, installed in ``<home>/.memestra``.

Declarative Cache
-----------------

The declarative cache is a file-based cache manually managed by users or
third-party packages. Its structure is very simple: to describe a Python file
whose path is ``<root>/numpy/random/__init__.py``, one need to drop a file in
``<prefix>/share/memestra/numpy/random/__init__.yml``. The yaml content looks
like the following:

.. code:: yaml

    deprecated: ['deprecated_function1', 'deprecated_function2:some reason']
    generator: manual
    name: numpy.random
    version: 1

- The ``deprecated`` field is the most important one. It contains a list of
  strings, each element being the name of a deprecated identifier. Text after
  the first (optional) ``:`` is usead as deprectation documentation.

- The ``generator`` field must be set to ``manual``.

- The ``name`` field is informative, it documents the cache entry and is usually
  set to the entry path.

- The ``version`` field is used to track compatibility with further format
  changes. Current value is ``1``.

When hitting an entry in the declarative cache, *memestra* does **not**
process the content of the file, and uses the entry content instead.


Automatic Cache
---------------

To avoid redundant computations, *memestra* also maintains a cache of the visited file
and the associated deprecation results.

To handle the cache, *memestra* provides a tool named ``memestra-cache``.

*Memestra*'s caching infrastructure is a file-based cache, located in
home/<user>/.memestra (RW). The key is a
hash of the file content and the value contains deprecation information, generator
used, etc.

There are two kind of keys: recursive and non-recursive. The recursive one also
uses the hash of imported modules, so that if an imported module changes, the
hash of the importing module also changes.

To interact with *memestra* caches:

**Positional arguments:**

``-set``

Set a cache entry in the automatic cache

``-list``

List cache entries for both caches

``-clear``

Remove all cache entries from the automatic cache

``-docparse``

Set cache entry from docstring in the automatic cache


**Optional arguments:**

  ``-h, --help``

  Show this help message and exit
