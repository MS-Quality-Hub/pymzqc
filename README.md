# MZQC python library
[![unit-tests](https://github.com/MS-Quality-hub/pymzqc/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/MS-Quality-hub/pymzqc/actions/workflows/unit_tests.yml)
[![Documentation Status](https://readthedocs.org/projects/pymzqc/badge/?version=latest)](https://pymzqc.readthedocs.io/en/latest/?badge=latest)
[![Docker Repository on Quay](https://img.shields.io/badge/container-ready-brightgreen.svg "Docker Repository on Quay")](https://quay.io/repository/mwalzer/pymzqc?tab=tags)
[![PyPi version](https://badgen.net/pypi/v/pymzqc/)](https://pypi.com/project/pymzqc)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MS-Quality-hub/pymzqc/blob/main/jupyter/mzqc_in_5/write_in_5_minutes.ipynb)

A python library to create and use mzQC files. Specifically, the library facilitates access to 
mzQC files in form of a **directly usable object representation of mzQC** and offers additional 
functionality to:
* serialise
* deserialise
* check syntax
* check semantics
* file-info
* experimental file-merging

**The library follows the formats versioning** (which is 'v(Major).(Minor).(Patch)').

This library implements python modules for (de-)serialisation and validity checks of the [PSI fileformat](http://www.psidev.info/groups/quality-control) [**mzQC**](https://hupo-psi.github.io/mzQC/). Find the specification document, examples, and and further documentation there.


## Install

### Latest Release
Most people will want to install the latest release version of pymzqc. Please install pymzqc via [**pypi**](https://pypi.org/project/pymzqc/): 
```
pip install pymzqc
```

### From Git
If you want a development version, use: 
```
pip install -U git+https://github.com/MS-Quality-hub/pymzqc.git#v1.0.0rc2
```
You can select a development branch of your choice by changing the command after the `.git#`

### Containers
However, we recommend using the ready-built [**containers**](https://quay.io/repository/mwalzer/pymzqc?tab=tags) to check out the latest updates.

## Online docs
To get a nice and simple overview of how pymzqc works, visit [here](https://pymzqc.readthedocs.io/en/latest/examples.html). 
If you've successfully installed the library and want to **jump right in and work on the library**, we suggest a peek at the [codestructure](https://pymzqc.readthedocs.io/en/latest/codestructure.html).

If you however just want to get your toes wet, or use it as-is, have a look at the interactive guides (below).

### Interactive pymzqc
Have a go with our [interactive python notebooks](jupyter/README.md) to explore what is possible.

## Development 
Contributions are welcome! (Just fork, develop, and open PR.)

### Repository structure
The python package's code is located in the `mzqc` folder, continuous testing code in `tests`, the documentation in `doc`. The libray-**use** container descriptions are in `containers`, if you want a container for library-**development**, you can use the container description within `.devcontainer`, more development presets can be found in `.vscode`. The `jupyter` and `accessories` folders are subprojects making use of the library. See their README in the respective sub-folders.

### Documentation
The code documentation style convention is of the type `Sphinx/numpy`.

