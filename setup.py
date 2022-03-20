import os
from glob import glob

from setuptools import find_packages, setup

from pynalyser import __name__, __version__

requirements = {}
for path in glob("requirements/*.txt"):
    with open(path) as file:
        name = os.path.basename(path)[:-4]
        requirements[name] = [line.strip() for line in file]

with open("README.md") as file:
    long_description = file.read()

github_link = "https://github.com/0dminnimda/{0}".format(__name__)

setup(
    name=__name__,
    version=__version__,
    description="Static Python Code Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="0dminnimda",
    author_email="0dminnimda.contact@gmail.com",
    url=github_link,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    license="MIT",
    project_urls={
        "Bug tracker": github_link + "/issues",
    },
    install_requires=requirements.pop("basic"),
    python_requires=">=3.6",
    extras_require=requirements,
    package_data={__name__: ["py.typed"]},
)
