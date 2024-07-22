#!/usr/bin/env python
import datetime as dt
from itertools import chain 
import click
from mzqc.MZQCFile import JsonSerialisable as mzqc_io

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
INFO = '''
The selected mzQC file has {n} different metrics registered, 
from {m} different runs and {k} defined 'sets', 
and it was created @ {d}.

'''
def print_help():
    """
    Print the help of the tool
    :return:
    """
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()

@click.version_option('v1BETA')
@click.command(short_help='mzQCFileInfo will report basic info on the mzQC file.')
@click.argument('infile', type=click.File('r'))
def mzqcfileinfo(infile):
    """
    Find out which metrics are available from the given mzQC file derived from which runs/sets.
    """
    if not infile:
        print_help()
    try:
        infofile = mzqc_io.FromJson(infile)
    except Exception as e:
        print("No mzQC structure detected in input!")
        print_help()

    rs = len(infofile.runQualities)
    ss = len(infofile.setQualities)
    mets = len({ metr.name for qm in chain(infofile.runQualities, infofile.setQualities) for metr in qm.qualityMetrics })
    print(INFO.format(n=mets, m=rs, k=ss, d=infofile.creationDate) )

    for n, run in enumerate(infofile.runQualities, start=1):
        mets = { (metr.name, metr.accession) for metr in run.qualityMetrics }

        files = [cd for cd in run.metadata.inputFiles]  # "location", "name", "fileFormat.name
        print("mzQC \"run\" #{n} was created for the input of the files:".format(n=n))
        for file in files:
            print(u"\t💾 {n} \n\t\t@ {l} \n\t\tof type".format(n=file.name, l=file.location),
                  getattr(file.fileFormat, "name", "UNSPECIFIED"))

        try:
            ct_str = next(iter([cd.value for infi in run.metadata.inputFiles for cd in infi.fileProperties if cd.accession=="MS:1000747"]))
            if ct_str.endswith("Z"):
                ct_str = ct_str[:-1]
            try:
                ct_datetime_object = dt.datetime.fromisoformat(ct_str)
                print(u"\t🕑 The MS run object was completed at", ct_datetime_object.isoformat())
            except Exception as e:
                print("\tCould not extract the run's completion time! Wrong format? Use the validator to find out.")
        except Exception as e:
            print("\tNo completion time found in mzQC for this MS run object.")
        print("\tMetrics:")
        print(*[u"\t 📈" + str(m) for m in mets], sep='\n',)

if __name__ == '__main__':
    mzqcfileinfo()
