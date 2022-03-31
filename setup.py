from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name='pymzqc',
    version='1.0.0rc1',
    packages=find_packages(exclude=("tests",)),
    author='Mathias Walzer',
    author_email='walzer@ebi.ack.uk',    
    url='https://github.com/MS-Quality-hub/pymzqc',
    description='Python library for the PSI-mzQC quality control file format.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "jsonschema",
        "numpy",
        "pandas",
        "pronto<2.2.1",
        "requests"
    ],
    setup_requires=['wheel'],
    python_requires='>=3.6',
    include_package_data=True,
    package_dir = {'': 'dist'}
)
