"""
This module is used to format variable to print
"""
__all__ = ['formatprint']


def listprint(listobj):
    """print list in a good format"""
    lstring = ""
    for entry in listobj:
        try:
            lstring += "\t%s\n" % entry
        except:
            print("print string failed ")
    return lstring

def dictprint(dictobj):
    """pritn dict in good format"""
    dstring = ""
    for key_ in dictobj.keys():
        dstring += "\t%s::\t\t%s\n" % (key_, dictobj[key_])
    return dstring

def formatprint(inputobj):
    """print objects in better format in log"""
    fstring = ""
    if isinstance(inputobj, str):  # pylint: disable=E0602
        fstring += "\t"+inputobj
    elif isinstance(inputobj, (list, tuple)):  # pylint: disable=E0602
        fstring += listprint(inputobj)
    elif isinstance(inputobj, dict):  # pylint: disable=E0602
        fstring += dictprint(inputobj)
    else:
        print("here is the type for input: %s" % type(inputobj))
    return fstring

def test():
    """test this library"""
    pass

def main():
    """ main function for lcoal usage"""
    pass

if __name__ == '__main__':
    main()
