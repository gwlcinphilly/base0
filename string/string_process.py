"""
This module is used for regular string process
"""
from _ast import If
__all__ = ['stringclean', "string2size",
           "size2string", "stringgroup",
           "stringtosize"]

# import default system library
import datetime
# import 3rd party library

# import shared library
from base0.constant import KBSIZE, MBSIZE, GBSIZE, EMPTYLINE

def stringclean(stringlist):
    """remove empty lines from string list"""
    result = []
    if isinstance(stringlist, list):
        result = [line for line in stringlist if line not in EMPTYLINE]
    elif isinstance(stringlist, str):
        result = [line for line in stringlist.split() if line not in EMPTYLINE]
    else:
        print("string type is not correct %s" % type(stringlist))
    return result

def stringgroup(stringlist, keywords, locations):
    """ group string by keywords"""
    stringlist = stringclean(stringlist)
    groups = {}
    for keyword in keywords:
        groups[keyword] = []
    groups['nogrouped'] = []
    nogrouped = True
    for line in stringlist:
        for keyword in keywords:
            if keyword in line:
                groups[keyword].append(line)
                nogrouped = False
                break
        if nogrouped:
            groups['nogrouped'].append(line)
        nogrouped = True
    stat = {}
    for keyword in keywords:
        stat[keyword] = len(groups[keyword])
    stat['nogrouped'] = len(groups['nogrouped'])
    stat['totallines'] = len(stringlist)
    groups['stat'] = stat
    return groups

def string2size(string):
    """convert string to a size"""
    size = 0
    try:
        size = int(string)
    except ValueError:
        if string[-1] in ['k', "K", "M", 'm']:
            ssize = int(string[:-1])
            if string[-1] in ["k", 'K']:
                size = ssize*KBSIZE
            elif string[-1] in ["M", 'm']:
                size = ssize*MBSIZE
        else:
            print("value %s is not valid " % string)
            return None
    return size

def size2string(size):
    """convert size to a readable string"""
    size = int(size)
    sizestring = ""
    if size > GBSIZE:
        sizestring = "%sGB" % round(float(size)/GBSIZE, 2)
    elif size > MBSIZE:
        sizestring = "%sMB" % round(float(size)/MBSIZE, 2)
    elif size > KBSIZE:
        sizestring = "%skB" % round(float(size)/KBSIZE, 2)
    else:
        sizestring = "%sBytes" % size
    return sizestring

def stringorlist(*kwargs):
    """ 
    this function will convert input to a list
    if input is a string, will split object with comma
    if input is a list, just return the list
    """
    returnlists = []
    for inputobj in kwargs:
        if isinstance(inputobj, str):
            returnlist = [_.strip() for _ in inputobj.split(",")]
        elif isinstance(inputobj, list):
            returnlist = inputobj
        returnlists.append(returnlist)
    return tuple(returnlists)

def stringtosize(sizestring):
    """ convert string to size"""
    size = 0
    if isinstance(sizestring,int):
        size = sizestring
    else:    
        if sizestring[-1] in ["k", "K"]:
            size = int(sizestring[:-1])*KBSIZE
        elif sizestring[-1] in ['m', "M"]:
            size = int(sizestring[:-1])*MBSIZE
        elif sizestring[-1] in ['g', "G"]:
            size = int(sizestring[:-1])*GBSIZE
        else:
            size = int(sizestring)
    return size

def string2time(timestring, timeformat, startyear=None):
    if isinstance(timestring,str): 
        cyear = datetime.datetime.now().date().year
        leapyear = False
        try:
            st = datetime.datetime.strptime(timestring,timeformat)
        except:
            # have to handle the leap year for 02/29
            import calendar
            year = int(startyear)
            for _ in range(4):
                if calendar.isleap(year):
                    break
                else:
                    year +=1
            if "02/29" in timestring:
                tformat = timeformat.split()[1]
                stime = datetime.datetime.strptime(timestring.split()[1], tformat)
                st = stime.replace(year=year, month=2, day=29)
                leapyear = True
        
        if startyear is not None and not leapyear:
            st = st.replace(year=int(startyear))        
    else:
        st = timestring
    return st

def list_int_stat(listobj, sizes=False):
    """print list of int static informations"""
    statinfo = {}
    stats = list(map(int, listobj))
    statinfo["len"] = len(stats)
    statinfo['min'] = min(stats)
    statinfo['max'] = max(stats)
    statinfo['sum'] = sum(stats)
    statinfo['ave'] = int(float(sum(stats))/statinfo["len"]) if statinfo["len"] > 0 else 0
    if sizes:
        for key_ in statinfo.keys():
            if key_ != "len":
                statinfo[key_] = size2string(statinfp[key_])
    return statinfo

def sizegroup(sizes):
    """group sizes for future static infos"""
    sizes = list(map(int, sizes))
    sizeinfos = {}
    onlybytes = []
    kbs = []
    mbs = []
    gbs = []

    qgroup, nqgroup = intergroup(sizes, KBSIZE)
    kbs += qgroup
    onlybytes += nqgroup
    tmplist = kbs
    kbs = []
    qgroup, nqgroup = intergroup(tmplist, MBSIZE)
    mbs += qgroup
    kbs += nqgroup
    tmplist = mbs
    mbs = []
    qgroup, nqgroup = intergroup(tmplist, GBSIZE)
    gbs += qgroup
    mbs += nqgroup
    sizeinfos = sizestat(sizes)
    if gbs != []:
        sizeinfos['gb'] = sizestat(gbs)
    if mbs != []:
        sizeinfos['mb'] = sizestat(mbs)
    if kbs != []:
        sizeinfos['kb'] = sizestat(kbs)
    if onlybytes != []:
        sizeinfos['bytes'] = sizestat(onlybytes)
    return sizeinfos

def datetime2json(objins):
    if isinstance(objins, datetime.datetime):
        return objins.__str__()


def test():
    """Test individaul library """
    pass

def main():
    """ main function for lcoal usage"""
    pass

if __name__ == '__main__':
    main()
