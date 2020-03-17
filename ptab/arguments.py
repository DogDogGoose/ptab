#
# Builder module for CGI arguments
#

import re
    
PTAB_MAX_LIMIT = 100

class ptoArgument(object):

    def factory(classtype):
        adjustedType = 'arg' + classtype

        if adjustedType.upper() == "ARGFILINGPARTY" : return argFilingParty()
        if adjustedType.upper() == "ARGPROCEEDINGNUMBER" : return argProceedingNumber()
        if adjustedType.upper() == "ARGTYPE" : return argType()
        if adjustedType.upper() == "ARGFILINGDATETIME" : return argFilingDatetime()
        if adjustedType.upper() == "ARGFILINGDATETIMEFROM" : return argFilingDatetimeFrom()
        if adjustedType.upper() == "ARGFILINGDATETIMETO" : return argFilingDatetimeTo()
        if adjustedType.upper() == "ARGFILINGDATEFROM" : return argFilingDateFrom()
        if adjustedType.upper() == "ARGLIMIT" : return argLimit()
        if adjustedType.upper() == "ARGOFFSET" : return argOffset()
        if adjustedType.upper() == "ARGSORTORDER" : return argSortOrder()
        if adjustedType.upper() == "ARGRECORDSTART" : return argRecordStart()
        if adjustedType.upper() == "ARGRECORDQUANTITY" : return argRecordQuantity()

        assert 0, "Bad argument creation: " + classtype

    factory = staticmethod(factory)

    def __str__(self):
        return self.argument + '=' + str(self.value)
    
    def __init__(self):
        self.argument = ''
        self.value = ''
        return

    def setValue(self, value):
        # children should verify values
        self.value = value
        return 1
    
class argFilingDateFrom(ptoArgument):
    def __init__(self):
        self.argument = 'filingDateFrom'
        self.value = ''

class argRecordQuantity(ptoArgument):
    def __init__(self):
        self.argument = 'recordTotalQuantity'
        self.value = 25

class argRecordStart(ptoArgument):
    def __init__(self):
        self.argument = 'recordStartNumber'
        self.value = 0

class argSortOrder(ptoArgument):
    def __init__(self):
        self.argument = 'sortOrderCategory'
        self.value = 'documentNumber'

    def setValue(self, value):
        self.value = 'documentNumber'

class argLimit(ptoArgument):
    def __init__(self):
        self.argument = 'limit'
        self.value = ''

    def setValue(self, value):
        if not value:
            self.value = PTAB_MAX_LIMIT

        if (value > PTAB_MAX_LIMIT):
            self.value = PTAB_MAX_LIMIT
        else:
            self.value = value

class argOffset(ptoArgument):
    def __init__(self):
        self.argument = 'offset'
        self.value = ''

class argFilingParty(ptoArgument):
    def __init__(self):
        self.argument = 'filingParty'
        self.value = ''

class argProceedingNumber(ptoArgument):
    def __init__(self):
        self.argument = 'proceedingNumber'
        self.value = ''

    def formatDocket(teststr):
        # regex = r"([a-zA-Z]+) (\d+)"
        regexCheckIPR = r"^IPR"
        match = re.search(regexCheckIPR, teststr)
        if match is None:
            teststr = 'IPR' + teststr

        regexCheckDocket = r"^(IPR|CBM)20\d{2}-\d{5}"
        match = re.search(regexCheckDocket, teststr)
        if match is None:
            return ''
        else:
            return teststr

    formatDocket = staticmethod(formatDocket)

    def setValue(self, value):
        formattedDktNumber = self.formatDocket(value)

        if len(formattedDktNumber) > 0:
            self.value = formattedDktNumber
            return True
        else:
            return False

class argType(ptoArgument):
    def __init__(self):
        self.argument = 'type'
        self.value = ''

class argFilingDatetime(ptoArgument):
    def __init__(self):
        self.argument = 'filingDatetime'
        self.value = ''

class argFilingDatetimeFrom(ptoArgument):
    def __init__(self):
        self.argument = 'filingDatetimeFrom'
        self.value = ''

class argFilingDatetimeTo(ptoArgument):
    def __init__(self):
        self.argument = 'filingDatetimeTo'
        self.value = ''

        
