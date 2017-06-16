# 
# Import local packages
#
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import ptab.cgi

goodPairs = {
	'trialNumber' : '2016-12345',
	'filingParty' : 'petitioner'
	}

testbuilder = ptab.cgi.builder()
if testbuilder.addArgument('trialNumber', '2016-12345'):
	print "Added."

if testbuilder.addArgument('filingParty', 'petitioner'):
	print "Added."

print testbuilder.getCGIStr()

