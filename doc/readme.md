# Documentation structure
bootstrap: `sphinx-quickstart`
N.B. source and build folders are kept separate!
Edit `doc/source/index.rst`, adding static rst like intro, etc. and code generated class documentation. Use `:glob:` for wildcards.
Build the from code generated documentation: `sphinx-apidoc -f -o doc/source/codegen mzqc`
Then, check the doc representation: `sphinx-build doc/source -W -b linkcheck -d _build/doctrees _build`
And finally, build html with `sphinx-build doc/source _build`



Writing documentation:
* https://rest-sphinx-memo.readthedocs.io/en/latest/ReST.html#rest-roles
* https://build-me-the-docs-please.readthedocs.io/en/latest/Using_Sphinx/UsingGraphicsAndDiagramsInSphinx.html
* https://stackoverflow.com/questions/9084173/how-to-underline-text-in-restructuredtext

Building:
* https://docs.readthedocs.io/en/stable/builds.html
* https://docs.readthedocs.io/en/stable/config-file/v2.html#supported-settings