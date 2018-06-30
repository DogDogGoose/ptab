
import requests
import string
import json
import shutil
import os
import re
import pprint

import cgi

#
# PTAB API
# 
docsURL = 'https://ptabdata.uspto.gov/ptab-api/documents'
trialsURL = 'https://ptabdata.uspto.gov/ptab-api/trials/'
dateURL = 'https://ptabdata.uspto.gov/ptab-api/trials?'

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
        self.dumpJson = False
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
        outfile = self.outdir + filename.replace('/', '-')

        if self.verbose:
            print ("\tDownloading (%s)" % outfile)

        if os.path.exists(outfile):
            print ("\tSKIPPING: %s already exists!" % outfile)
            return 0

        if self.download:
            r = requests.get(fileurl, stream=True, verify=self.verify)
            if r.status_code == 200:
                with open(outfile, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)        
        else:
            print ("Downloads Disabled: URL <%s>" % fileurl    )

        return 1

    def getDocumentListURL (self, dktnum):
        return self.buildTrialsUrl(dktnum);

        #
        # Alternative way to search dockets. This sometimes works better, 
        # though the PTAB interface for both trials and documents can be flaky.
        #

        # default to IPR over CBM
        # docketstr = dktnum if re.search(r'(IPR|CBM)20\d{2}-\d{5}', dktnum) else ("IPR" + dktnum)

        # cgimaker = cgi.builder()
        # if not cgimaker.addArgument('trialNumber', docketstr):
            # print ("\tERROR: improper docket %s" % docketstr)
            # return ''

        # return docsURL + cgimaker.getCGIStr()

    def buildTrialsUrl(self, dktnum, zip=False):
        docketstr = ''
        if re.search(r'(IPR|CBM)20\d{2}-\d{5}', dktnum):
            docketstr = dktnum
        else:
            # default to IPR over CBM
            docketstr = "IPR" + dktnum

        targetUrl = trialsURL + docketstr

        if zip:
            targetUrl += postfixdoczip
        else:
            targetUrl += postfixdocs

        # add a high limit to the results
        # TODO: add iterative paging functionality using offset to page through results
        # targetUrl += "?limit=100"

        return targetUrl

    def buildDocsUrl(self, filterarguments):
        testbuilder = cgi.builder()
        for key, val in filterarguments.iteritems():
            if testbuilder.addArgument(key, val):
                if self.verbose: print ("Added (%s : %s)." % (key, val))
            else:
                print ("ERROR: FAILED TO ADD (%s : %s)." % (key, val) )
        return docsURL + testbuilder.getCGIStr()

    def curlJson(self, targetUrl):
        if self.verbose:
            print ("Getting <%s>" % targetUrl)

        result = 0
        if self.verify:
            # TODO
            # dktmeta = requests.get(targetUrl, cert=ptabcert)
            result = 0
        else:
            try:
                result = requests.get(targetUrl, verify=self.verify)
                print ("Curl got result (%s)" % result)
            except ValueError:
                print ("ERROR: Could Not access URL.")

        return result


    def downloadJsonLinks(self, jsonstr):
        parsedjson = json.loads(jsonstr)
        results = parsedjson.get('results')

        if (self.dumpJson):
                    text_file = open("JSONdump.txt", "w")
                    text_file.write(jsonstr)
                    text_file.close()

        if (results is None):
            return 0

        for document in results:
            # print ("Number, title: (%s, %s)" % (document['documentNumber'], document['title']))
            fname_raw = document['documentNumber'] + " - " + document['title']
            fname = fname_raw.replace('.', '') + ".pdf"

            if self.verbose:
                print ("Processing (%s)" % fname)
        
            for link in document['links']:
                if link['rel'] == 'download':
                    # account for an error in formatting that sometimes appears in the ptab json feed
                    docurlstr = re.sub(r'ptab-api[\\/]+ptab-api', 'ptab-api', link['href'])

                    if self.verbose:
                        print ("\tURL <%s>" % docurlstr)
                    self.curlFile(docurlstr, fname)

        return len (parsedjson['results'])
            
    def getDocsInDocket(self, dktnum):
        results = self.curlJson( self.getDocumentListURL(dktnum) )

        if results:
            numDocs = self.downloadJsonLinks(results.text)
        else:
            print ("ERROR: Could not read URL")
            return

        if self.verbose:
            print ("Found %s documents." % numDocs)

        return
    
    def searchDocuments(self, filterarguments):
        targetUrl = self.buildDocsUrl(filterarguments)

        if self.verbose:
            print ("Using search string:" + "\t" + targetUrl)

        results = self.curlJson(targetUrl)
        if results:
            numDocs = self.downloadJsonLinks(results.text)
        else:
            print ("ERROR: Could not read URL")
            return

        if self.verbose:
            print ("Found %s documents." % numDocs)

        return

    def locateDocketsByParty(self, partyname, earliestfilingdate):
        searchDateUrl = self.buildDateUrl(earliestfilingdate)
        if self.verbose:
            print ("Using search string:" + "\t" + searchDateUrl)

        results = self.curlJson(searchDateUrl)
        if results:
            dockets = self.filterJsonResultsByParty(results.text, partyname)

        else:
            print ("ERROR: Could not read URL")
            return

        if self.verbose:
            print ("Found %s dockets." % dockets)

        return

    def buildDateUrl(self, earliestfilingdate, offset=0):
        if not earliestfilingdate:
            earliestfilingdate = "2012-09-16" # enactment date

        searchObj = re.search( r'^\d{4}-\d{2}-\d{2}$', earliestfilingdate, re.I)
        if searchObj:
            print ("Using earliest filing date of %s" % earliestfilingdate)
        else:
            searchObj = re.search( r'^\d{4}$', earliestfilingdate, re.I)
            if searchObj:
                year = earliestfilingdate
                earliestfilingdate = year + "-01-01"
                print ("Year %s provided; using earliest filing date of %s" % (year, earliestfilingdate))

            else:
                print ("ERROR: Invalid starting date (%s)" % earliestfilingdate)

        querybuilder = cgi.builder()
        querybuilder.addArgument('filingDateFrom', earliestfilingdate)
        querybuilder.addArgument('limit')
        querybuilder.addArgument('offset', offset)

        return dateURL + querybuilder.getCGIStr()

    ########
    def filterJsonResultsByParty(self, jsonstr, partyname):
        parsedjson = json.loads(jsonstr)
        results = parsedjson.get('results')

        if (self.dumpJson):
                    text_file = open("JSONdump.txt", "w")
                    text_file.write(jsonstr)
                    text_file.close()

        if (results is None):
            return []

        # A more elegant way to filter, but it's not guaranteed that there is a patent owner or petitioner name...?
        filteredlist = filter(lambda x: re.search(r'' + re.escape(partyname), x.get('petitionerPartyName', '') + x.get('patentOwnerName', ''), re.IGNORECASE), results)

        # Safer filter function
        for proceeding in filteredlist:
            petitionerNameRaw = proceeding.get('petitionerPartyName', '[OMITTED]') 
            poNameRaw = proceeding.get('patentOwnerName', '[OMITTED]') 
            trialNumber = proceeding.get('trialNumber')
            status = proceeding.get('prosecutionStatus')
        
            print ("* %s v %s (%s)" % (petitionerNameRaw, poNameRaw, trialNumber))

        return len (parsedjson['results'])

