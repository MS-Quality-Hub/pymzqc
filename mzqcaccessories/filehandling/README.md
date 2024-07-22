## Fileinfo
```
mzqc-fileinfo [OPTIONS] INFILE
```

The fileinfo tool is a CLI tool built on [click](https://click.palletsprojects.com/).
Its purpose is simple as are its' call options.
Given a single mzQC file, it will produce a summary of the file's contents: 
which runs and sets are included and with which metrics.
For example:

```
The selected mzQC file has 5 different metrics registered, 
from 1 different runs and 0 defined 'sets', 
and it was created @ 2020-12-01 11:56:34+00:00.

mzQC "run" #1 was created for the input of the files:
        💾 CPTAC_CompRef_00_iTRAQ_01_2Feb12_Cougar_11-10-09.trfr.t3 
                @ ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2014/09/PXD000966/CPTAC_CompRef_00_iTRAQ_01_2Feb12_Cougar_11-10-09.raw/CPTAC_CompRef_00_iTRAQ_01_2Feb12_Cougar_11-10-09.trfr.t3.mzML 
                of type mzML format
        🕑 The MS run object was completed at 2012-02-03T11:00:41
        Metrics:
         📈('number of MS2 spectra', 'MS:4000060')
         📈('number of chromatograms', 'MS:4000071')
         📈('m/z acquisition range', 'MS:4000069')
         📈('number of MS1 spectra', 'MS:4000059')
         📈('retention time acquisition range', 'MS:4000070')
```

Please get more info on usage with the `--help` option.

## Filemerger
```
mzqc-filemerger [OPTIONS] [MZQC_INPUT]... MZQC_OUTPUT
```

> [!NOTE]  
> Tool in beta stage of development.

The filemerger tool is a CLI tool built on [click](https://click.palletsprojects.com/).
Its purpose is to merge one or more mzQC files.
The tool accepts multiple files or CLI wildcards as input and takes the last filename as target destination for the merge product.

For example: `mzqc-filemerger *.mzqc temp_test.mzqc`

| :warning: |
|:----------|
| Merging operations are limited for beta. In case no _clear_ run or set correspondence can be established, the merge will fall back to a conservative merge into lists of separate runs.|
