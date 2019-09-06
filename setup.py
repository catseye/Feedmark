from distutils.core import setup


setup(
    name='Feedmark',
    version='0.9',
    description='Tools for processing documents in Feedmark, a curation-oriented subset of Markdown',
    author='Chris Pressey',
    author_email='packages@catseye.tc',
    url='https://catseye.tc/node/Feedmark',
    packages=['feedmark'],
    package_dir={'': 'src'},
    scripts=['bin/feedmark'],
)
