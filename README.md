# MZQC python library
[![unit-tests](https://github.com/MS-Quality-hub/pymzqc/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/MS-Quality-hub/pymzqc/actions/workflows/unit_tests.yml)
[![Documentation Status](https://readthedocs.org/projects/pymzqc/badge/?version=latest)](https://pymzqc.readthedocs.io/en/latest/?badge=latest)
[![Docker Repository on Quay](https://img.shields.io/badge/container-ready-brightgreen.svg "Docker Repository on Quay")](https://quay.io/repository/mwalzer/pymzqc?tab=tags)
[![pypi](https://img.shields.io/pypi/wheel/pymzqc)](https://pypi.org/project/pymzqc/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/MS-Quality-hub/pymzqc/v1.0.0rc1?filepath=jupyter%2FMZQC_in_5_minutes.ipynb)

A python library to use mzQC files. Specifically, have a usable object representation of mzQC that can
* serialise
* deserialise
* check syntax
* check semantics

**The library follows the formats versioning** (which is 'v(Major).(Minor).(Patch)').

This library implements python modules for (de-)serialisation and validity checks of the [PSI fileformat](http://www.psidev.info/groups/quality-control) [**mzQC**](https://hupo-psi.github.io/mzQC/). Find the specification document, examples, and and further documentation there.


## Install

### Latest Release
Most people will want to install the latest release version of pymzqc. Please install pymzqc via [**pypi**](https://pypi.org/project/pymzqc/): 
```
pip install pymzqc
```

### From Git
If you want the latest development version, use: 
```
pip install -U git+https://github.com/MS-Quality-hub/pymzqc.git#egg=pymzqc
```
### Containers
However, we recommend using the ready-built [**containers**](https://quay.io/repository/mwalzer/pymzqc?tab=tags) to check out the latest updates.

## Documentation
To get a nice and simple overview of how pymzqc works, visit [here](https://pymzqc.readthedocs.io/en/latest/examples.html). 
successfully installed the library and want to **jump right in and use the library**, we suggest the a peek at the [codestructure](https://pymzqc.readthedocs.io/en/latest/codestructure.html).

If you however just want to get your toes wet, have a look at the interactive guides.

### Interactive pymzqc
Have a go with our [interactive python notebooks](jupyter/README.md) to explore what is possible.


## Development 

Contributions are welcome! (Just fork, develop, and open PR.)

### Repository structure
The python package's code is located in the `mzqc` folder, continuous testing code in `tests`, the documentation in `doc`. The libray-**use** container descriptions are in `containers`, if you want a container for library-**development**, you can use the container description within `.devcontainer`, more development presets can be found in `.vscode`. The `jupyter` and `accessories` folders are subprojects making use of the library. See their README in the respective sub-folders.

### Documentation
The code documentation style convention is of the type `Sphinx/numpy`.

