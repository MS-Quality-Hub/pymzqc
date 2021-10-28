# MZQC python library
![](https://github.com/bigbio/mzqc-pylib/workflows/unit-tests/badge.svg)
![](https://github.com/bigbio/mzqc-pylib/workflows/release-container/badge.svg)
![](https://readthedocs.org/projects/mzqc-pylib/badge/?version=v1.0.0&style=flat)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/bigbio/mzqc-pylib/v1.0.0?filepath=jupyter%2FMZQC_in_5_minutes.ipynb)

A python library to use mzQC files. Specifically, have a usable object representation of mzQC that can
* serialise
* deserialise
* syntactic checks
* semantic checks

## Install
Please install mzqc-pylib via [PyPI](https://pypi.org/). If you want the latest development install
```
pip install -U git+https://github.com/bigbio/mzqc-pylib.git#egg=mzqc-pylib
```
However, we recommend using the [containers](https://quay.io/repository/mwalzer/mzqc-pylib) to check out the latest updates.

## Documentation
To get a nice and simple overview of how the mzQC-pylib works, visit [here](https://mzqc-pylib.readthedocs.io).
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
Have a go with our [interactive python notebook](https://mybinder.org/v2/gh/bigbio/mzqc-pylib/v1.0.0?filepath=jupyter%2FMZQC_in_5_minutes.ipynb) to explore what is possible. ([static version](https://github.com/bigbio/mzqc-pylib/blob/master/jupyter/MZQC_in_5_minutes.ipynb))
