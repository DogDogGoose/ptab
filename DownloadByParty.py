import argparse

# 
# Import local packages
#
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    print(path.dirname(path.abspath(__file__)))
    sys.path.append(path.dirname(path.abspath(__file__)))

import ptab.core

###########################
# Main
###########################
print ("Downloading all IPR dockets for a party filed since a certain date...")

parser = argparse.ArgumentParser(description='Grab and properly name documents from PTAB dockets.')
parser.add_argument('--verbose', '-v', type=bool, default=True, help='Wow much talk.', dest='verbose')
parser.add_argument('--outdir', '-o', required=False, help='Parent directory to build tree of output docket folders')
parser.add_argument('--party', '-p', required=True, help='Base name of the party to search for')
parser.add_argument('--startdate', '-s', required=False, help='Starting date of search, based on filing date of petition (Format YYYY-MM-DD)')
parser.add_argument('--test', action='store_true', help="Test only; don't download PDF files")
parser.add_argument('--dump', action='store_true', help="Save JSON to file for debug")

args = parser.parse_args()

myptab = ptab.core.ptabgrab(True)
if args.test: myptab.download = False
if args.dump: myptab.dumpJson = True

if not args.outdir:
    args.outdir = "temp/"

myptab.setOutputDir(args.outdir)
myptab.getDocketsByParty(args.party, args.startdate)


