#!/usr/local/bin/python

import argparse
import ptab.core

###########################
# Main
###########################
parser = argparse.ArgumentParser(description='Grab and properly name documents from PTAB dockets.')
parser.add_argument('--verbose', '-v', type=bool, default=False, help='Wow much talk.', dest='verbose')
parser.add_argument('--dkt', '-d', required=True, help='Docket Number')
parser.add_argument('--outdir', '-o', required=False, help='Place to put output PDF files')
args = parser.parse_args()

myptab = ptab.core.ptabgrab(True)
myptab.setOutputDir(args.outdir)
myptab.getDocsInDocket(args.dkt)

