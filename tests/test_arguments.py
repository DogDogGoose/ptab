# 
# Import local packages
#
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import ptab.arguments

testTrialNumber = ptab.arguments.ptoArgument.factory('trialNumber')

baddies = ['211-01234', 'ABC-01234', '2017-0123']
for baddy in baddies:
	print "Testing malformed docket (%s)" % baddy
	if testTrialNumber.setValue(baddy):
		print "\tError: a malformed docket number was set, when it should have been rejected (%s)" % baddy
	else:
		print "\tSuccess: Malformed docket num rejected (%s)" % baddy

goodies = ['2016-12345', 'IPR2017-11111']
for goody in goodies:
	print "Testing malformed docket (%s)" % goody
	if testTrialNumber.setValue(goody):
		print "\tSuucess: set docket (%s)" % goody
	else:
		print "\tError: a correct docket number was rejected (%s)" % goody

testFilingParty = ptab.arguments.ptoArgument.factory('filingParty')
testType = ptab.arguments.ptoArgument.factory('type')
testFilingDatetime = ptab.arguments.ptoArgument.factory('filingDatetime')
testFilingDatetimeFrom = ptab.arguments.ptoArgument.factory('filingDatetimeFrom')
testFilingDatetimeTo = ptab.arguments.ptoArgument.factory('filingDatetimeTo')


