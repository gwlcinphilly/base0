"""
This library is used to process xml file related operations
"""
from logging import FileHandler
__all__ = []




def xml2dict(xmlfile, xmlroot=None):
    """
    convert xml format to python dict
    need to verify this after migrate to python 3.6
    """
    """
    script_location = os.path.dirname(os.path.realpath(__file__))
    try:
        converter = xml2json('%s/xml/%s' % (script_location, xmlfile),\
                             encoding="utf-8")
    except:
        converter = xml2json('%s/%s' % (script_location, xmlfile),\
                                     encoding="utf-8")
    constantsraw = json.loads(converter.get_json())[xmlroot]
#    convert next level entry to correct format based on the tag:

    try:
        for constant in constantsraw.keys():
            for key_ in constant.keys():
                if constant[key_].keys() == "LIST":
                    liststring = constant[key_]['LIST'].strip()[1:-1]
                    constant[key_] = liststring.split(",")
                elif constant[key_].keys() == "DICT":
                    pass
                else:
                    pass
    except:
        pass

    try:
        del constantsraw[xmlroot]
    except:
        pass
    return constantsraw
    """
    import xmltodict
    with open(xmlfile) as filehandlerins:
        xmlcontent = xmltodict.parse(filehandlerins.read())
    if xmlroot is None: 
        xmlroot = xmlcontent.keys()
    
    print(xmlcontent)
    print(xmlcontent[xmlroot])
    
def test():
    """test this library"""
    import os
    xmlfiles =[filename for filename in os.listdir("../xml") \
               if filename[-4:] in [".xml",".XML"]] 
    for xmlfile in xmlfiles:
        dictins = xml2dict(f"../xml/{xmlfile}")

def main():
    """ main function for lcoal usage"""
    test()

if __name__ == '__main__':
    main()
