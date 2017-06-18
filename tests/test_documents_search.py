import argparse

# 
# Import local packages
#
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import ptab.core

goodPairs = {
	'trialNumber' : '2016-12345',
	'filingParty' : 'petitioner'
	}

###########################
# Main
###########################
print "Testing documents search API..."

myptab = ptab.core.ptabgrab(True)

# disable downloads for test
myptab.download = False

myptab.setOutputDir("../test")
myptab.verbose = True
myptab.searchDocuments(goodPairs)


