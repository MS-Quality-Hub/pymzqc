## Local validation
```
mzqc-validator [OPTIONS] INFILE
```
The validator tool is a CLI tool built on [click](https://click.palletsprojects.com/).
It will generate a joint validation of syntax and semantics of a given mzQC input.
The output is in json format. 
The validator will segment the validation report into lists of the following categories:
- "input files": reports duplicate input files for sets or runs or inconsistent file name and location
- "label uniqueness": checking if run and set labels are unique within the file,
- "metric use": reports duplicate metric use within a set or run, and, if applicable, table consistency, unit use, 
    "ontology load errors": all controlled vocabularies that could not be loaded,
- "ontology term errors": checks for ambiguous terms found in multiple of the used controlled vocabularies, terms used not found in any given controlled vocabulary, and correct name, definition, and reference usage,
- "schema validation": report all elements not corresponding to the mzQC schema",
- "ontology validation": in case any non-online controlled vocabularies were used.