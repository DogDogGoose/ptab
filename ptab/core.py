import sys
import requests
import requests_cache
import string
import unicodedata
import json
import shutil
import os
import re
import pprint
import pathvalidate

import ptab.cgi

#
# PTAB API
# 
baseURL = 'https://developer.uspto.gov/ptab-api'
docsURL = 'https://developer.uspto.gov/ptab-api/documents'
trialsURL = 'https://developer.uspto.gov/ptab-api/proceedings'
dateURL = 'https://developer.uspto.gov/ptab-api/proceedings'

postfixdocs = '/documents'
postfixdoczip = '/documents.zip'
# ptabcert = "~/scripts/ptab/ptab.pem"

PTAB_MAX_RESULTS = 25

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

        requests_cache.install_cache(cache_name='ptab_cache', backend='sqlite', expire_after=36000) # expire after 10 hours
        requests.packages.urllib3.disable_warnings()

    def __str__(self):
        return "%s documents found." % self.getNumDocs()

    def getOutputDir(self):
        return self.outdir

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

    def cleanUnicodeString(self, filename, filterForPath):
        filteredUnicode = filename.replace('/', '-').replace('"', '').replace("'", "") if (filterForPath) else filename 
        filteredAscii = unicodedata.normalize('NFKC', filteredUnicode).encode('ascii', 'ignore')
        return pathvalidate.sanitize_filename(filteredAscii.decode('utf-8'))

    # 
    # curlFile
    # used to save files
    #
    def curlFile(self, fileurl, filename):
        # filesystype = sys.getfilesystemencoding() # should generally be 'utf-8'

        cleanfilename = self.outdir + self.cleanUnicodeString(filename, 1)

        if self.verbose:
            print ("\tDownloading (%s)" % cleanfilename)

        if os.path.exists(cleanfilename):
            print ("\tSKIPPING: %s already exists!" % cleanfilename)
            return 0

        if self.download:
            myheaders = {'Accept-Encoding': 'deflate'}
            r = requests.get(fileurl, stream=True, verify=self.verify, headers=myheaders)
            if r.status_code == 200:
                with open(cleanfilename, 'wb') as f:
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

    def buildTrialsUrl(self, dktnum, startingRecordNumber = -1):
        dktnum = dktnum.upper()
        docketstr = ''
        if re.search(r'(IPR|CBM)20\d{2}-\d{5}', dktnum):
            docketstr = dktnum
        else:
            # default to IPR over CBM
            docketstr = "IPR" + dktnum

        testbuilder = ptab.cgi.builder()
        testbuilder.addArgument("sortOrder")

        if testbuilder.addArgument("proceedingNumber", docketstr):
            if self.verbose: 
                print ("Added (%s : %s)." % ('proceedingNumber', docketstr))
        else:
            print ("ERROR: FAILED TO ADD (%s : %s)." % (key, val) )

        # TODO: add iterative paging functionality using offset to page through results
        if startingRecordNumber >= 0:
            if self.verbose:
                print ("Iterating starting with record number (%i)" % startingRecordNumber)
            testbuilder.addArgument('recordStart', startingRecordNumber)
            testbuilder.addArgument('recordQuantity', PTAB_MAX_RESULTS)


        targetUrl = docsURL + testbuilder.getCGIStr()
        return targetUrl

    #
    #
    def buildDocsUrl(self, filterarguments):
        testbuilder = ptab.cgi.builder()
        for key, val in filterarguments.iteritems():
            if testbuilder.addArgument(key, val):
                if self.verbose: print ("Added (%s : %s)." % (key, val))
            else:
                print ("ERROR: FAILED TO ADD (%s : %s)." % (key, val) )
        return docsURL + testbuilder.getCGIStr()

    #
    #
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

    def parseJsonList(self, jsonstr):
        parsedjson = json.loads(jsonstr)

        if (self.dumpJson):
            json_dump_text = jsonstr.encode('ascii', 'ignore')
            text_file = open("JSONdump.txt", "a")
            text_file.write(json_dump_text.decode('utf-8'))
            text_file.close()

        return parsedjson

    #
    # Downloads all links in the json list
    #
    def downloadJsonLinks(self, jsonstr):
        jsondata = self.parseJsonList(jsonstr)
        resultsList = jsondata.get('results')

        for document in resultsList:
            # print ("Number, title: (%s, %s)" % (document['documentNumber'], document['title']))
            fname_raw = document.get('documentNumber').zfill(4) + " - " + document.get('documentTitleText')
            fname = fname_raw.replace('.', '') + ".pdf"

            if self.verbose:
                print ("Processing (%s)" % self.cleanUnicodeString(fname, 0))
        
            docID = document.get('documentIdentifier')
            downloadLink = baseURL + '/documents/{documentIdentifier}/download'.replace('{documentIdentifier}', docID)
            if self.verbose:
                print ("\tURL <%s>" % downloadLink)

            self.curlFile(downloadLink, fname)

        retval = dict()
        retval['downloadedRecords'] = len (resultsList)
        retval['totalRecords'] = jsondata.get('recordTotalQuantity')
        return retval
            
    #
    # Downloads all documents in the docket
    # 
    def getDocsInDocket(self, dktnum):

        allDocsDownloaded = False 
        currentRecord = 0

        while not allDocsDownloaded:
            ptabJsonList = self.curlJson( self.buildTrialsUrl(dktnum, currentRecord) )

            if ptabJsonList:
                status = self.downloadJsonLinks(ptabJsonList.text)
                numDocs = status['downloadedRecords']
                totalDocs = status['totalRecords']

                if self.verbose:
                    print ("Found %s documents." % numDocs)
                    print ("Found %s total docs in docket." % totalDocs)

                if currentRecord >= totalDocs:
                    allDocsDownloaded = True
                else:
                    currentRecord += PTAB_MAX_RESULTS

                next

            else:
                print ("ERROR: Could not read URL")
                next

    #
    # Get a specific paper in a docket
    def getPaper(self, dktnum, papernum):
        if self.verbose:
            print ("Getting Paper (%s) from Docket (%s)" % (papernum, dktnum))

        ptabJsonList = self.curlJson( self.getDocumentListURL(dktnum) )

        if ptabJsonList:
            rawresults = self.parseJsonList(ptabJsonList.text)
            docketDocsList = rawresults.get('results')

            ptabObj = self.findPaper(papernum, docketDocsList)
            if (ptabObj):
                downloadUrl = self.getLink(ptabObj)

                if self.verbose:
                    print ("\tURL <%s>" % downloadUrl)

                fname_raw = ptabObj.get('documentNumber') + " - " + ptabObj.get('title')
                fname = fname_raw.replace('.', '') + ".pdf"
                return self.curlFile(downloadUrl, fname)

            else:
                print ("ERROR: Could not find paper (%s)" % papernum)
                return 0

        else:
            print ("ERROR: getPaper() could not read URL for docket")
            return

    def findPaper(self, paperNumber, docketList):
        if (len(docketList) > 1):
            hitList = list(filter(lambda xlist: xlist.get('documentNumber') == paperNumber, docketList))

            if (len(hitList) == 1):
                return hitList[0];
            elif (len(hitList > 1)):
                print ("Warning: findPaper() found more than 1 paper number (%s); using first result" % paperNumber)
                return hitList[0];
            else:
                print ("ERROR: findPaper() could not find paper number (%s)" % paperNumber)
                return 0

        else:
            return 0

    def getLink(self, ptabResultObj):

        for link in ptabResultObj.get('links'):
            if link['rel'] == 'download':
                # account for an error in formatting that sometimes appears in the ptab json feed
                return re.sub(r'ptab-api[\\/]+ptab-api', 'ptab-api', link['href'])

        # if program falls out of the for loop
        return 0

    # 
    # In development...
    #
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


    # 
    # Main access point. Gets all dockets with a certain party as petitioner or po
    #
    def getDocketsByParty(self, partyname, earliestfilingdate):
        dockets = self.locateDocketsByParty(partyname, earliestfilingdate)

        baseOutDir = self.getOutputDir()

        for dock in dockets:
            (petitioner, patentowner, dkt, status) = dock[0:4]
            print ("* {0} v {1} ({2}) - {3}".format(petitioner, patentowner, dkt, status))
            docketOutDir = self.makeSafeFilename("{0}-{1} v {2}".format(dkt, petitioner, patentowner))
            cleanDocketOutDir = docketOutDir.encode('ascii', 'ignore')

            newdir = os.path.join(baseOutDir, cleanDocketOutDir)
            self.setOutputDir(newdir)
            self.getDocsInDocket(dkt)

    # 
    # Locates all dockets with a certain party as petitioner or po
    # Recursive
    # 
    def locateDocketsByParty(self, partyname, earliestfilingdate, offset=0):
        searchDateUrl = self.buildDateUrl(earliestfilingdate, offset)
        if self.verbose:
            print ("Using search string:" + "\t" + searchDateUrl)

        results = self.curlJson(searchDateUrl)
        if results:
            dockets = []
            (totalCount, nextOffset) = self.filterJsonResultsByParty(results.text, partyname, dockets)

            # This is how we know we have more to do
            if (totalCount >= nextOffset):
                newDockets = self.locateDocketsByParty(partyname, earliestfilingdate, offset=nextOffset)
                if (len(newDockets) > 0):
                    dockets += newDockets

            return dockets

        else:
            print ("ERROR: Could not read URL")
            return []

    #
    # Makes a date query for ptab API
    # 
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

        querybuilder = ptab.cgi.builder()
        querybuilder.addArgument('filingDateFrom', earliestfilingdate)
        querybuilder.addArgument('limit')
        querybuilder.addArgument('offset', offset)

        return dateURL + querybuilder.getCGIStr()

    #
    # takes a JSON list from the all trials query, filters by party name
    #
    def filterJsonResultsByParty(self, jsonstr, partyname, dockets):
        parsedjson = json.loads(jsonstr)
        results = parsedjson.get('results')
        numResults = len(results)

        if (self.dumpJson):
                    json_dump_text = jsonstr.encode('ascii', 'ignore')

                    text_file = open("JSONdump.txt", "a")
                    text_file.write(json_dump_text.decode('utf-8'))
                    text_file.close()

        if (results is None):
            return []

        filteredlist = filter(lambda x: re.search(r'' + re.escape(partyname), x.get('petitionerPartyName', '') + x.get('patentOwnerName', ''), re.IGNORECASE), results)

        # consider changing this loop to a map function
        for proceeding in filteredlist:
            petitionerNameRaw = proceeding.get('petitionerPartyName', '[OMITTED]') 
            poNameRaw = proceeding.get('patentOwnerName', '[OMITTED]') 
            trialNumber = proceeding.get('proceedingNumber')
            status = proceeding.get('prosecutionStatus')
        
            dockets.append([petitionerNameRaw, poNameRaw, trialNumber, status])
        
        # Now figure out how many items are left
        meta = parsedjson.get('metadata')
        currentLimit = meta.get("limit")
        currentOffset = meta.get("offset")
        currentCount = meta.get("count")

        print ("Limit (%s), Offset (%s), Count (%s)" % (currentLimit, currentOffset, currentCount))

        return (currentCount, currentOffset + currentLimit)

    #
    # Make a string safe
    # 
    def makeSafeFilename(self, inputFilename):   
        try:
            safechars = string.letters + string.digits + " -_."
            return filter(lambda c: c in safechars, inputFilename)

        except:
            return ""  
            pass
