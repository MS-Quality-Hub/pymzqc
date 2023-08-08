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
        "jsonschema>=3.2.0",
        "numpy",
        "pandas>=1.1.5",
        "pronto",
        "requests>=2.27.1"
    ],
    setup_requires=['wheel'],
    python_requires='>=3.6',
    include_package_data=True,
    scripts=['accessories/heroku/mzqc_online_validator.py', 'accessories/offline/mzqc_offline_validator.py']
    # entry_points = {
    #     'console_scripts': [
    #         'mzQC-online-validator=accessories.heroku.mzqc_online_validator:start',
    #         'mzQC-offline-validator=accessories.offline.mzqc_offline_validator:start'
    #     ],
    # }
    # package_dir = {'': 'dist/'}
)
