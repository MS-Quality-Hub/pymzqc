#!/usr/bin/env python
import os
from os.path import basename
from os.path import join
from os.path import dirname
import click
import datetime as dt
from itertools import chain 
from mzqc.MZQCFile import JsonSerialisable as mzqc_io


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
INFO = '''
The selected mzQC file has {n} different metrics registered, from {m} different runs and {k} defined 'sets'. 
'''
def print_help():
    """
    Print the help of the tool
    :return:
    """
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()

@click.command(short_help='mzQCFileInfo will report basic info on the mzQC file.')
@click.argument('input', type=click.File('r'))
def mzqcfileinfo(input):
    """
    Find out which metrics are available from the given mzQC file derived from which runs/sets.
    """
    if not input:
        print_help()
    try:
        infofile = mzqc_io.FromJson(input)
    except Exception as e:
        print("No mzQC structure detected in input!")
        print_help()

    rs = len(infofile.runQualities)
    ss = len(infofile.setQualities)
    mets = { metr.name for qm in chain(infofile.runQualities, infofile.setQualities) for metr in qm.qualityMetrics }

    print(INFO.format(n=len(mets), m=rs, k=ss) )
    print("Metrics:")
    print(*enumerate(list(mets)), sep='\n')

if __name__ == '__main__':
    mzqcfileinfo()