Memestra-cache
==============

Memestra uses a cache to speedup some computations. To handle the cache, memestra installs a tool named ``memestra-cache``.

Memestra's caching infrastructure is a file-based cache, located in home/<user>/.memestra (RW) and in <prefix>/memestra/cache (RO). The key is a hash of the file content and the value is deprecation information, generator used, etc.

There are two kind of keys: recursive and non-recursive. The recursive one also uses the hash of imported modules, so that if an imported module changes, the hash of the importing module aslo changes.

To interact with memestra cache:

**Positional arguments:**

``-set``

Set a cache entry

``-list``

List cache entries

``-clear``

Remove all cache entries

``-docparse``

Set cache entry from docstring


**Optional arguments:**

  ``-h, --help``

  Show this help message and exit
