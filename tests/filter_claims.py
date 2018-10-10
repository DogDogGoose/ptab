import argparse

# 
# Import local packages
#
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    # print(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import ptab.claims

###########################
# Main
###########################
parser = argparse.ArgumentParser(description='Filter claim list from google patents. Reads from stdin.')
parser.add_argument('--verbose', '-v', type=bool, default=False, help='Wow much talk.', dest='verbose')
parser.add_argument('--outdir', '-o', required=False, help='Place to put output text file')
parser.add_argument('--keep', '-o', required=True, help='list of patent claims to keep')

args = parser.parse_args()

myclaims = ptab.claims.patentclaims()
myclaims.readClaims()


