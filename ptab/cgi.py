#
# Module for building CGI commands for PTAB API
#
# filingParty	: {petitioner, patent_owner, board, potential_patent_owner}
# trialNumber	: e.g., IPR2016-00037, CBM2014-22245.
# type		: {notice, Mandatory Notice, motion, opposition, power of attorney, rehearing request, order, Judge Working File, Petion, etc.}
# filingDatetime : Filters by the date (YYYY-MM-DD) a document was filed.
# filingDatetimeFrom	
# filingDatetimeTo	
#
# Example URL
# https://ptabdata.uspto.gov/ptab-api/documents?filingParty=sony&type=motion
#

import arguments

class builder(object):
	"""
	builds strings for the ptab rest api
	"""
	def __init__(self):
		self.arguments = []

	def addArgument(self, arg, value):
		newobj = arguments.ptoArgument.factory(arg)
		newobj.setValue(value)

		if (newobj):
			self.arguments.append(newobj)
			return True
		else:
			return False

	def getCGIStrNoQuestion(self):
		if len (self.arguments) > 0:
			return '&'.join(map(lambda x:str(x), self.arguments))
		else:
			return ''
		
	def getCGIStr(self):
		return '?' + self.getCGIStrNoQuestion()
