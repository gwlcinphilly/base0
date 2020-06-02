"""
This module is basic shared  lib which doesn't have any ohter 3rd party library

"""
__all__ = ["get_log", "timecounter", "Appbasic",]
# import default system library

import os
import datetime
import logging

from itertools import groupby
from time import time, sleep
# import 3rd party library

# import shared library
from base0.constant import  LOGFORMAT_STRING
from base0.exception import AppException

def get_log(logname=None,path=None, level="INFO"):
    """
    This function will create log. If commvualt obj is not present, will
    create a log on local. This will help for individual tools and local debug
    """
    logginglevel  = getattr(logging, level)
    if logname:
        path, logname = os.path.split(logname)
        moduelname = logname.split('.py')[0]
        logname = f"{path}/log/{moduelname}.log"
    else:
        moduelname = "localtest"
        if path is None:
            locallogpath = "./log"
        else:
            locallogpath = path
        if not os.path.exists(locallogpath):
            os.makedirs(locallogpath)
        if logname is None:
            logname = os.path.join(locallogpath, "localtest.log")
    formatter = logging.Formatter(LOGFORMAT_STRING)
    if __name__ == "__builtin__":
        print("use as builtin")
    else:
#       if the log is call in this module, will create a localtest logger
        logger = logging.getLogger(moduelname)
        hdlr = logging.FileHandler(logname)
        hdlr.setFormatter(formatter)
        if logger.handlers == []:
            logger.addHandler(hdlr)
        logger.setLevel(logginglevel)
        logger.propagate = False
    return logger


def timecounter(ptime=None, timeformat=None, delay=None):
    """
    return time and check the time different
    also can working as sleep with delay option
    """
    returnvalue = None
    if delay is not None:
        sleep(delay)
    if ptime is None:
        if timeformat is None:
            returnvalue = time()
        elif timeformat == "ISO":
            returnvalue = datetime.datetime.now().isoformat().split('.')[0]
        elif timeformat == "filename":
            isostring = datetime.datetime.now().isoformat().split('.')[0].split("T")
            returnvalue = isostring[0]+"_"+"".join(isostring[1].split(":"))
        elif timeformat == "date":
            isostring = datetime.datetime.now().isoformat().split('.')[0].split("T")
            returnvalue = isostring[0]
    else:
        ctime = time()
        returnvalue = ctime-ptime
    return returnvalue


def intergroup(internumbers, limitvalue):
    """This function will group internal based on the limitvalue"""
    qualifygroup = []
    noqualifygroup = []
    for key_, groupentry in groupby(internumbers, key=lambda n: n > limitvalue):
        if key_:
            qualifygroup = list(groupentry)
        else:
            noqualifygroup = list(groupentry)
    return qualifygroup, noqualifygroup

class Appbasic:
    """Basic class for AppBasic class,handle common things"""

    def __init__(self, name):
        self.appname = name
        self.log = get_log()

    def __str__(self):
        return self.appname

    def __repr__(self):
        return f"I am an instance of \
                {self.appname} at address {hex(id(self))}"

    def arg_assign(self, kwargs, required_fields, optional_fields):
        """ Assign class attribute"""
        all_keys = kwargs.keys()
        for field in required_fields:
            if field in all_keys:
                setattr(self, field, kwargs[field])
            else:
                raise AppException(self.appname, 201,
                                   f"input doens't have {field}")

        for field in optional_fields:
            if field in all_keys:
                setattr(self, field, kwargs[field])
            else:
                setattr(self, field, None)
