#!/usr/local/bin/python
import logging
from itertools import groupby
from itertools import chain
import click
from mzqc import MZQCFile as qc

def print_help():
    """
    Print the help of the tool
    :return:
    """
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()

def dedupe(list_of_cvparam_like):
    """
    deduplicate lists of mzqc elements that are derived
    from cvparam (i.e. they have an accession attribute)
    """
    if not(all([isinstance(x, qc.CvParameter) for x in list_of_cvparam_like]) or\
        all([isinstance(x, qc.ControlledVocabulary) for x in list_of_cvparam_like]) or\
        all([isinstance(x, qc.InputFile) for x in list_of_cvparam_like])):
        raise TypeError("List of elements to deduplicate contains non-CvParameter types.")

    if all([isinstance(x, qc.ControlledVocabulary) for x in list_of_cvparam_like]):
        return list({x.name+x.version: x for x in list_of_cvparam_like}.values())
    elif all([isinstance(x, qc.InputFile) for x in list_of_cvparam_like]):
        return list({x.name: x for x in list_of_cvparam_like}.values())
    else:
        return list({x.accession: x for x in list_of_cvparam_like}.values())

def merge_into_single_run(runs):
    """
    merge run quality objects if from the same run
    runs are considerd the same if location, name, and format match
    returns both files back, 
        - first is the merger result or the first input if they dont match, 
        - second is always second input
    """
    for f in runs: 
        logging.debug(f.metadata)

    metrics = dedupe(list(chain.from_iterable([x.qualityMetrics for x in runs])))
    asw = dedupe(list(chain.from_iterable([x.metadata.analysisSoftware for x in runs])))
    labels = '+'.join({x.metadata.label for x in runs if x.metadata.label != ''})
    inf = dedupe(list(chain.from_iterable([x.metadata.inputFiles for x in runs])))

    return qc.RunQuality(metadata=qc.MetaDataParameters(
            label=labels, inputFiles=inf, analysisSoftware=asw),
        qualityMetrics=metrics)

def match_and_merge_sets_files(sets):
    pass

@click.version_option('v1BETA')
@click.command(short_help='A simple mzQC file merger using pymzqc assuming file metadata is compatible. mzQC files will be merged, where possible runs matched and metrics combined.')
@click.argument('mzqc_input', nargs=-1, type=click.Path(exists=True,readable=True, dir_okay=False) )  # help="The mzqc files to merge"
@click.argument('mzqc_output', type=click.Path(writable=True, dir_okay=False) )  # help="The output path for the resulting mzqc"
@click.option('--compare', type=click.Choice(['metadata', 'location', 'name'], case_sensitive=False),
    default='metadata', show_default=True,
    required=False, help="Level of comparison determining which run's metrics need to be merged into one run. For `metadata`, whole metadata objects must be the same, for `location` the location attributes must be the same, and for `name` only the name attribute must be the same.")
@click.option('--log', type=click.Choice(['debug', 'info', 'warn'], case_sensitive=False),
    default='warn', show_default=True,
    required=False, help="Log detail level. (verbosity: debug>info>warn)")
def mzqcfilemerger(mzqc_output, mzqc_input, compare, log):
    # set loglevel - switch to match-case for py3.10+
    lev = {'debug': logging.DEBUG,
     'info': logging.INFO,
     'warn': logging.WARN }
    logging.basicConfig(format='%(levelname)s:%(message)s', level=lev[log])

    cvs = list()
    cname = set()
    caddress = set()
    to_merge = list()
    for fn in mzqc_input:
        with open(fn, "r") as file:
            mzqc = qc.JsonSerialisable.FromJson(file)
            to_merge.extend(mzqc.runQualities)
            cvs.extend(mzqc.controlledVocabularies)
            cname.add(mzqc.contactName)
            caddress.add(mzqc.contactAddress)
            if len(mzqc.setQualities)>0:
                # stop if there are msetQualities in either file - we don't cover that here yet - see match_and_merge_sets_files
                raise IndexError("Cannot merge mzqc with sets yet!")

    if len(to_merge) < 2:
        raise IndexError("Need at least 2 mzQC files to merge!")

    merged = []

    # same metadata - why does it need merging in the first place?
    if compare == 'metadata':
        for key, group in groupby(to_merge, lambda x: x.metadata):
            merged.append(merge_into_single_run(list(group)))

    # scenario where you apply different tools to the same file, some might have additional inputFiles though
    elif compare == 'location':
        reversedorder = {'MS:1000562':0,'MS:1000563':1,'MS:1000584':2} #ABI WIFF format/Thermo RAW format/mzML format; NOTE that any other format will have 0 as default so will be sorted to back when applying reverse sort
        for run in to_merge:
            run.metadata.inputFiles.sort(key=lambda x: reversedorder.get(x.fileFormat.accession, 0), reverse=True)
        for key, group in groupby(to_merge, lambda x: x.metadata.inputFiles[0].location):  # this might be an issue but sorting of the metadata input files might help
            merged.append(merge_into_single_run(list(group)))

    # scenario where you apply different tools to the same file but through workflow circumstances the location is registered as different
    else:  # == 'name'
        reversedorder = {'MS:1000562':0,'MS:1000563':1,'MS:1000584':2} #ABI WIFF format/Thermo RAW format/mzML format; NOTE that any other format will have 0 as default so will be sorted to back when applying reverse sort
        for run in to_merge:
            run.metadata.inputFiles.sort(key=lambda x: reversedorder.get(x.fileFormat.accession, 0), reverse=True)
        for key, group in groupby(to_merge, lambda x: x.metadata.inputFiles[0].name):
            merged.append(merge_into_single_run(list(group)))

    with open(mzqc_output, "w") as file:
        file.write(qc.JsonSerialisable.ToJson(
            qc.MzQcFile(description="Merged from multiple mzqc files", 
                        contactName='+'.join(cname),
                        contactAddress='+'.join(caddress),
                        version="v1.0",
                        controlledVocabularies=dedupe(cvs), 
                        runQualities=merged), readability=1))

    click.echo("Files merged. Thank you for doing QC!")

if __name__ == '__main__':
    mzqcfilemerger()
