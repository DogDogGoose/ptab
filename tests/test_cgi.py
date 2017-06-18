# 
# Import local packages
#
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import ptab.cgi
import ptab.core

goodPairs = {
	'trialNumber' : '2016-12345',
	'filingParty' : 'petitioner'
	}

testbuilder = ptab.cgi.builder()

for key, val in goodPairs.iteritems():
	if testbuilder.addArgument(key, val):
		print "Added (%s : %s)." % (key, val)
	else:
		print "ERROR: FAILED TO ADD (%s : %s)." % (key, val) 

print testbuilder.getCGIStr()

grabber = ptab.core.ptabgrab()
grabber.verbose = True
print grabber.buildDocsUrl(goodPairs)


