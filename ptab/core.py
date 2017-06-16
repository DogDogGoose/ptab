
import requests
import string
import json
import shutil
import os

#
# PTAB API
# 
docsURL = 'https://ptabdata.uspto.gov/ptab-api/documents'
trialsURL = 'https://ptabdata.uspto.gov/ptab-api/trials/'
postfixdocs = '/documents'
postfixdoczip = '/documents.zip'
# ptabcert = "~/scripts/ptab/ptab.pem"

###########################
class ptabgrab(object):
	"""
	utilizes the ptab rest api
	"""
	def __new__(cls, verbose=False):
		newobj = object.__new__(cls)
		newobj.verbose = verbose

		return newobj 

	def __init__(self, verbose=False):
		self.verbose = verbose
		self.verify = False
		self.outdir = ''
		self.download = True
		requests.packages.urllib3.disable_warnings()

	def __str__(self):
		return "%s documents found." % self.getNumDocs()

	def setOutputDir(self, odir):
		newodir = os.path.join(odir, '')
		if not os.path.isdir(newodir):
			os.makedirs(newodir)

		self.outdir = newodir
		return
	
	# TODO
	def setCertificate(certpath):
		# check path
		# verify cert
		self.verify = True

	# TODO
	def getNumDocs():
		return 0

	def curlFile(self, fileurl, filename):
		outfile = self.outdir + filename
		if self.verbose:
			print "Downloading (%s)" % outfile

		if self.download:
			r = requests.get(fileurl, stream=True, verify=self.verify)
			if r.status_code == 200:
				with open(outfile, 'wb') as f:
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)        
		else:
			print "Downloads Disabled: URL <%s>" % fileurl	

		return 1

	def buildTrialsUrl(self, dktnum, zip=False):
		docketstr = "IPR" + dktnum
		targetUrl = trialsURL + docketstr
		if zip:
			targetUrl += postfixdoczip
		else:
			targetUrl += postfixdocs

		return targetUrl

	# TODO
	def buildDocsURl(self):
		targetUrl = ""
		return targetUrl


	def curlJson(self, targetUrl):
		if self.verbose:
			print "Getting <%s>" % targetUrl

		if self.verify:
			# TODO
			# dktmeta = requests.get(targetUrl, cert=ptabcert)
			return 0
		else:
			return requests.get(targetUrl, verify=self.verify)


	def parseJson(self, jsonstr):
		parsedjson = json.loads(jsonstr)
		for document in parsedjson['results']:
			fname_raw = document['documentNumber'] + " - " + document['title']
			fname = string.replace(fname_raw, '.', '') + ".pdf"

			if self.verbose:
				print "Processing (%s)" % fname
		
			for link in document['links']:
				if link['rel'] == 'download':
					if self.verbose:
						print "\tURL <%s>" % link['href']

					self.curlFile(link['href'], fname)

		return len (parsedjson['results'])
			
	def getDocsInDocket(self, dktnum):
		results = self.curlJson( self.buildTrialsUrl(dktnum) )
		numDocs = self.parseJson(results.text)

		if self.verbose:
			print "Found %s documents." % numDocs

		return

