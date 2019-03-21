"""
This module is used to handle all exception in base0
"""
__all__ = ["exceptionlist", "Errorlogging", "AppException"]
import json
import os

def exceptionlist():
    exceptions = {}
    return exceptions

Exception_List  =   exceptionlist()


def Errorlogging(error):
    StartString = "\n"+"-"*32+"ERROR"+"-"*30+"\n"
    EndString =  "\n"+"-"*65+"\n"
    try: 
        if Exception_List[error.appname][error.Value]['action'] in ["",None]:
            exceptiondetail =   Exception_List[error.appname][error.Value]['action']+"\n<br/>"
        else:   
            exceptiondetail     = "App type is:\t"+error.appname+"\n<br/>Error Code is:\t"+str(error.Value)
            exceptiondetail     = exceptiondetail+"\n<br/>Error Detail is:\t"+Exception_List[error.appname][error.Value]['detail']
            exceptiondetail     = exceptiondetail+"\n<br/>Error Section is:\t"+Exception_List[error.appname][error.Value]['section']
        exceptiondetail     = exceptiondetail+"\n<br/>Error message is:\t"+str(error.Message)                                     
        ErrorString        =    "%s\
                            Test Case failed with: %s\n\
                            ErrCode:\t%s\n\
                            Message:\t%s\
                            %s" % (StartString,
                                error.appname,
                                error.Value,
                                exceptiondetail,
                                EndString)
    except:
        exceptiondetail    = error
        ErrorString        =    "%s\
                            Test Case failed with: %s\n\
                            ErrCode:\t%s\n\
                            Message:\t%s\
                            %s" % (StartString,
                                "Unknown",
                                "Unknown",
                                exceptiondetail,
                                EndString)        
    return ErrorString,exceptiondetai

class AppException(Exception):
    
    def __init__(self,appname,value,message=""):
        self.appname    =   appname
        self.Value      =   value
        self.Message    =   message
        return None
    
    def __str__(self):
        return self.Message
