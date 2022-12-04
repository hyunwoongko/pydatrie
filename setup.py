import os

from setuptools import setup, find_packages

version = None
author = None

with open(os.path.join("pydatrie", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.strip().startswith("__version__"):
            version = line.split("=")[1].strip().replace('"', "").replace("'", "")
        if line.strip().startswith("__author__"):
            author = line.split("=")[1].strip().replace('"', "").replace("'", "")

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pydatrie",
    version=version,
    author=author,
    author_email="kevin.ko@tunib.ai",
    url="https://github.com/hyunwoongko/pydatrie",
    license="Apache 2.0 License",
    description="Pure Python implementation of DARTS (Double ARray Trie System)",
    long_description_content_type="text/markdown",
    platforms=["any"],
    long_description=long_description,
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3",
    zip_safe=False,
    include_package_data=True,
)
