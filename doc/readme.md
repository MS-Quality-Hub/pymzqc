# Documentation structure
bootstrap: `sphinx-quickstart`
N.B. source and build folders are kept separate!
Edit `doc/source/index.rst`, adding static rst like intro, etc. and code generated class documentation. Use `:glob:` for wildcards.
Build the from code generated documentation: `sphinx-apidoc -f -o doc/source/_codegen mzqc`
Then, check the doc representation: `sphinx-build doc/source -W -b linkcheck -d doc/build/doctrees doc/build`
And finally, build html with `sphinx-build doc/source doc/build`



Writing documentation:
* https://stackoverflow.com/questions/9084173/how-to-underline-text-in-restructuredtext