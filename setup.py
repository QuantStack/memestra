from setuptools import setup

kw = {"test_suite": "tests"}

dev_reqs = open("requirements-dev.txt").read().splitlines()
extras_require = {"test": dev_reqs, "dev": dev_reqs}

setup(
    name="memestra",
    version="0.0.1",
    packages=["memestra"],
    description="Track calls to deprecated functions.",
    long_description="""
A linter that tracks reference to deprecated functions.

Memestra walks through your code base and tracks reference to function marks
with a given decorator.""",
    author="serge-sans-paille",
    author_email="serge.guelton@telecom-bretagne.eu",
    url="https://github.com/QuantStack/memestra",
    license="BSD 3-Clause",
    install_requires=open("requirements.txt").read().splitlines(),
    extras_require=extras_require,
    entry_points={'console_scripts':
                  ['memestra = memestra.memestra:run',
                   'memestra-cache = memestra.caching:run'],
                  'memestra.plugins':
                  [".ipynb = memestra.nbmemestra:register", ],
                  },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.4",
    **kw
)
