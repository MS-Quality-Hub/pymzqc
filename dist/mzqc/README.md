# Build Instructions
This file only exists to provide container-based builds an existing dist folder setup, i.e.:
```
mkdir -p dist/mzqc
python3 -m build --sdist
python3 -m build --wheel
```