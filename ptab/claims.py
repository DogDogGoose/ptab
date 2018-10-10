
import fileinput

import string
import os
import re
import pprint
import pathvalidate

###########################
class patentclaims(object):
    """
    processes patent claims from google
    """
    def __new__(cls, verbose=False):
        newobj = object.__new__(cls)
        newobj.verbose = verbose

        return newobj 

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.outdir = ''

    def __str__(self):
        return ""

    def readClaims(self):
        for line in fileinput.input():
            pass

    def getOutputDir(self):
        return self.outdir

    def setOutputDir(self, odir):
        newodir = os.path.join(odir, '')
        if not os.path.isdir(newodir):
            os.makedirs(newodir)

        self.outdir = newodir
        return
    
