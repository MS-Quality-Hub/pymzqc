#!/usr/bin/env python
from typing import Dict, List
import click
from pronto import Ontology, Term
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
from mzqc.MZQCFile import MzQcFile, BaseQuality, RunQuality, SetQuality, QualityMetric, MetaDataParameters, CvParameter

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def rfix_term(val, vocs):
    if hasattr(val, 'accession'):
        if val.description == "":
            terms: List[Term] = list(filter(None, [voc.get(val.accession) for voc in vocs.values()]))
            if terms:
                val.description = next(iter(terms)).definition
    elif isinstance(val, List):
        for v in val:
            rfix_term(v, vocs)
    elif isinstance(val, (MzQcFile,SetQuality,RunQuality,MetaDataParameters)):
        for _, v in vars(val).items():
            rfix_term(v, vocs)

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
@click.argument('outfile', type=click.File('w'))
def mzqcfixdescriptions(infile, outfile):
    """
    Find out which metrics are available from the given mzQC file derived from which runs/sets.
    """
    if not infile:
        print_help()
    try:
        fixfile = mzqc_io.FromJson(infile)
    except Exception:
        print("No mzQC structure detected in input!")
        print_help()

    vocs:Dict[str,Ontology] = dict()
    for cve in fixfile.controlledVocabularies:
        try:
            vocs[cve.name] = Ontology(cve.uri, import_depth=0)
        except Exception:
            pass
    rfix_term(fixfile, vocs)
    outfile.write(mzqc_io.ToJson(fixfile,readability=2))

if __name__ == '__main__':
    mzqcfixdescriptions()
