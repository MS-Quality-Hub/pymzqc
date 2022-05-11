# MZQC python library
[![unit-tests](https://github.com/MS-Quality-hub/pymzqc/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/MS-Quality-hub/pymzqc/actions/workflows/unit_tests.yml)
[![Docker Repository on Quay](https://quay.io/repository/mwalzer/pymzqc/status "Docker Repository on Quay")](https://quay.io/repository/mwalzer/pymzqc)
![](https://readthedocs.org/projects/pymzqc/badge/?version=v1.0.0rc1&style=flat)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/MS-Quality-hub/pymzqc/v1.0.0rc1?filepath=jupyter%2FMZQC_in_5_minutes.ipynb)

A python library to use mzQC files. Specifically, have a usable object representation of mzQC that can
* serialise
* deserialise
* syntactic checks
* semantic checks

## Install
Please install pymzqc via [PyPI](https://pypi.org/). If you want the latest development install
```
pip install -U git+https://github.com/MS-Quality-hub/pymzqc.git#egg=pymzqc
```
However, we recommend using the [containers](https://quay.io/repository/mwalzer/pymzqc) to check out the latest updates.

## Documentation
To get a nice and simple overview of how pymzqc works, visit [here](https://pymzqc.readthedocs.io).
The code documentation style convention is of the type "Sphinx/numpy".
If you however have successfully installed the library and want to **jump right in and use the library**, we suggest the [interactive guide](#5min-interactive-guide).

## Development 

### Repository structure
The python package's code is located in the `mzqc` folder, continuous testing code in `tests`, the documentation in `doc`. The **libray-use** container descriptions are in `containers`, if you want to **develop** for the library with a container, please use the container description within `.devcontainer`.

### Contribution
Contributions are welcome! (Fork and open PR)

## MZQC
This library implements python modules for (de-)serialisation and validity checks of the [PSI fileformat mzQC](http://www.psidev.info/groups/quality-control). To see the raw fileformat, including json schema and specification documentation, see https://github.com/HUPO-PSI/mzQC/. **The library follows the formats versioning**(which is 'v(Major).(Minor).(Patch)').

## 5min interactive guide
Have a go with our [interactive python notebook](https://mybinder.org/v2/gh/MS-Quality-hub/pymzqc/v1.0RC?filepath=jupyter%2Fmzqc_in_5%2FMZQC_in_5_minutes.ipynb) to explore what is possible. ([static version](https://github.com/MS-Quality-hub/pymzqc/blob/main/jupyter/mzqc_in_5/MZQC_in_5_minutes.ipynb))
