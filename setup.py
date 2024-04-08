from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pymzqc',
    version='1.0.0rc2',
    packages=find_packages(exclude=("tests",)),
    author='Mathias Walzer',
    author_email='walzer@ebi.ack.uk',
    url='https://github.com/MS-Quality-hub/pymzqc',
    description='Python library for the PSI-mzQC quality control file format.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "jsonschema>=3.2.0",
        # Note: in order to validate JSON date-time type expressions the rfc3339 libs need to be present (otherwise the Formatchecker for date-time won't be initialised)
        "strict-rfc3339",
        "rfc3339-validator",
        "numpy",
        "pandas>=1.1.5",
        "pronto",
        "requests>=2.27.1",
        "click",
    ],
    setup_requires=['wheel', 'Click'],
    python_requires='>=3.8',
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'mzqc-fileinfo=mzqcaccessories.filehandling.mzqc_fileinfo:mzqcfileinfo',
            'mzqc-filemerger=mzqcaccessories.filehandling.mzqc_filemerger:mzqcfilemerger',
            # 'mzQC-online-validator=mzqconlinevalidator.mzqc_online_validator:app.run',
            # Note: onlinevalidator has extra dependencies not covered by this setup!
            #       See accessories/onlinevalidator/requirements.txt!
            'mzqc-validator=mzqcaccessories.offlinevalidator.mzqc_offline_validator:start'
        ],
    }
)
