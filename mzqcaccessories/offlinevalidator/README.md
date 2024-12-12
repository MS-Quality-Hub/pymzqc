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

The tools first reads the `INFILE` and will produce a first error if the file can't be read. 
This can be because the *JSON* is illformatted or the structure contains elements that cannot be parsed by pythons Json library.
In case you encounter such an error, we suggest you use a JSON syntax checker. 
E.g.: `check-jsonschema --schemafile ./schema/mzqc_schema.json INFILE`  [see [the pypi package for the tool](https://pypi.org/project/check-jsonschema/)].
The validator then goes on to retrieve all `controlledVocabularies` (CV) listed in `INFILE`. 
For successful validation the used CV therefore needs to be accesible via a stable URL and all terms used in the `INFILE` must be included in the CVs.
The validator will produce an error for each unknown term it encounters. 
Method of lookup is accession.
The validator also checks if the name of the term used corresponds to the CV entry.
The validator then checks the `INFILE` contents asper the previously described categories.