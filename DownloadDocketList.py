import argparse
import fileinput

# 
# Import local packages
#
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    # print(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import ptab.core

# dockets = ['2016-01183']

###########################
# Main
###########################
print ("Downloading list of dockets from STDIN...")

parser = argparse.ArgumentParser(description='Grab and properly name documents from PTAB dockets.')
parser.add_argument('--verbose', '-v', type=bool, default=True, help='Wow much talk.', dest='verbose')
parser.add_argument('--outdir', '-o', required=False, help='Place to put output PDF files')
parser.add_argument('--dd', action='store_true', help="Don't download PDF files")

args = parser.parse_args()

myptab = ptab.core.ptabgrab(True)
if args.dd: myptab.download = False

if not args.outdir:
    args.outdir = "temp" 

# Read from stdin
for line in fileinput.input('-'):
    docket = line.strip()
    outputDir = args.outdir + "/" + docket.upper()

    if docket.isspace():
        next

    myptab.setOutputDir(outputDir)
    myptab.getDocsInDocket(docket)

