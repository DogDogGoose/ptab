import argparse

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
print ("Running basic test...")

parser = argparse.ArgumentParser(description='Grab and properly name documents from PTAB dockets.')
parser.add_argument('--verbose', '-v', type=bool, default=True, help='Wow much talk.', dest='verbose')
parser.add_argument('--dkt', '-d', required=True, help='Docket Number')
parser.add_argument('--outdir', '-o', required=False, help='Place to put output PDF files')
parser.add_argument('--dd', action='store_true', help="Don't download PDF files")
parser.add_argument('--dump', action='store_true', help="Save JSON to file for debug")

args = parser.parse_args()

myptab = ptab.core.ptabgrab(True)
if args.dd: myptab.download = False
if args.dump: myptab.dumpJson = True

if not args.outdir:
    args.outdir = "../temp/" + args.dkt

myptab.setOutputDir(args.outdir)
myptab.getDocsInDocket(args.dkt)


