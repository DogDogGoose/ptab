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
print ("Downloading paper in a docket...")

parser = argparse.ArgumentParser(description='Get a specific paper from a docket.')
parser.add_argument('--verbose', '-v', type=bool, default=True, help='Wow much talk.', dest='verbose')
parser.add_argument('--outdir', '-o', required=False, help='Parent directory to write downloaded file')
parser.add_argument('--docket', '-d', required=True, help='Docket number')
parser.add_argument('--paper', '-p', required=True, help='Paper number')
parser.add_argument('--test', action='store_true', help="Test only; don't download PDF files")
parser.add_argument('--dump', action='store_true', help="Save JSON to file for debug")

args = parser.parse_args()

myptab = ptab.core.ptabgrab(True)
if args.test: myptab.download = False
if args.dump: myptab.dumpJson = True

if not args.outdir:
    args.outdir = "temp/"

myptab.setOutputDir(args.outdir)
myptab.getPaper(args.docket, args.paper)


