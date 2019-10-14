import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Feedmark',
    version='0.9',
    description='Definition of Feedmark, a curation-oriented subset of Markdown, and tools for processing it',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Chris Pressey',
    author_email='packages@catseye.tc',
    url='https://catseye.tc/node/Feedmark',
    packages=['feedmark'],
    package_dir={'': 'src'},
    scripts=['bin/feedmark'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
)
