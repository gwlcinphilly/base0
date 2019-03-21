"""
define constant used in all shared library
"""
__all__ = ["WEBFILENAME",
           "KBSIZE", "MBSIZE", "GBSIZE",
           "STRINGTYPE", "EMPTYLINE",
           "PYLINTMESSAGE", "PYLINTCHECKVARS"]
# define Static
LOGFORMAT_STRING = ('%(asctime)-25sLine-%(lineno)-7d%(module)-15s'\
                 '%(funcName)-20s%(levelname)-7s%(message)s')

WEBFILENAME = ['html', 'htm', 'xml', 'txt']
KBSIZE = 1024
MBSIZE = 1024*KBSIZE
GBSIZE = 1024*MBSIZE
STRINGTYPE = ["letter", 'utf8', 'unicode', 'regular', "chineseword"]
EMPTYLINE = ["", "\n", "\r", "\r\n"]
# class related constant
PYLINTMESSAGE = ["Trailing whitespace", "Exactly one space required after comma",
                 "Undefined variable", "imported from constant",
                 "Too many branches", "Final newline missing",
                 "Missing function docstring", "Invalid variable name",
                 "Unused argument",
                 "Specify string format arguments as logging function parameters"]

PYLINTCHECKVARS = ['appname', 'script', 'modulename', 'rate', 'pre_rate']
STRINGTYPE      =   ['regular','unicode','utf8']
RFC822_FIELDS       =   ['MIME-Version', 'Received', 'From', 'To', 'CC', 'Subject', 'Date', 'Message-ID', 'X-MIMETrack']
OFFICEFILENAME  =   ['docx','xlsx','ppt','msg','doc']
