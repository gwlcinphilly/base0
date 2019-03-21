"""
This module is used to generate simple data
"""
__all__ = ["DataGenerator",
           "random_string", "letter_generator", "string_generator",
           "unicode_generator", "byte_range",
           "file_write", "file_generator"]

# import default system library
import string
import random
import os
import codecs
import json

# import 3rd party library

# import shared library
from base0.constant import STRINGTYPE
from base0.baselibs import Appbasic
from base0.string.string_process import stringtosize

def random_string(sizerange=None, contenttype=None, size=None):
    """ generate string basic information """
    if contenttype is None:
        contenttype = random.choice(STRINGTYPE)
    if sizerange is None:
        sizerange = [random.randint(1024, 2048), random.randint(2049, 4096)]
    if size is None:
        size = random.randint(sizerange[0], sizerange[1])
    else:
        size = stringtosize(size)
    return contenttype, size

def letter_generator(size=1024,
                     chars=string.ascii_letters+string.digits):
    """generate string with letter only"""
    return ''.join(random.choice(chars) for _ in range(size))

def string_generator(size=1024, chars=string.printable,
                     charset=None):
    """ generate string with charset """
    if charset is not None:
        string_ = "".join([random.choice(charset) for _ in range(size)])
    else:
        string_ = ''.join([random.choice(chars) for _ in range(size)])
    return string_

def unicode_generator(size=1024):
    """ generate unicode string """
    get_char = chr
    include_ranges = [(0x0021, 0x0021), (0x0023, 0x0026),
                      (0x0028, 0x007E), (0x00A1, 0x00AC),
                      (0x00AE, 0x00FF), (0x0100, 0x017F),
                      (0x0180, 0x024F), (0x2C60, 0x2C7F),
                      (0x16A0, 0x16F0), (0x0370, 0x0377),
                      (0x037A, 0x037E), (0x0384, 0x038A),
                      (0x038C, 0x038C)]

    alphabet = [get_char(code_point) for current_range in include_ranges
                for code_point in range(current_range[0],
                                        current_range[1] + 1)]
    return ''.join(random.choice(alphabet) for i in range(size))

def byte_range(first, last):
    """ set byte range list """
    return list(range(first, last+1))

def file_write(content, contenttype, folder, filename=None):
    """ write cotnent to a file """
    if filename is None:
        if contenttype in ["regular"]:
            filename = letter_generator(8)+".txt"
        elif contenttype in ["unicode", "utf8"] or \
            contenttype.startswith("chinese"):
            filename = letter_generator(8)+"."+contenttype+".txt"
    filepath = os.path.join(folder, filename)
    if contenttype in ["regular"]:
        with open(filepath, 'w') as filehandle:
            filehandle.write(content)
    elif contenttype in ["unicode", "utf8"] or \
        contenttype.startswith("chinese"):
        with codecs.open(filepath, 'w', 'utf-8-sig') as filehandle:
            filehandle.write(content)
    return  filename

def file_generator(sizerange, filenum, contenttype, folder="."):
    """Generate a file """
    filelist = []
    for _ in range(filenum):
        contenttype, size = random_string(sizerange=sizerange,
                                          contenttype=contenttype)
        content = string_generator(size, contenttype)
        filename = file_write(content, contenttype, folder)
        filelist.append(filename)
    return filelist

def randomword(letter=None):
    """ generate a random word from dictionary
    https://svnweb.freebsd.org/csrg/share/dict/words?view=co
    https://github.com/SaiWebApps/RandomWordGenerator
    will read the source and do it later
    """
    if letter is None:
        print("pick the first letter")
    else:
        pass

class DataGenerator(Appbasic):
    """ class to generator regular data """

    def __init__(self):
        """Initial basic class define"""
        Appbasic.__init__(self, self.__class__.__name__)
        self.utf8_first_values = byte_range(0x00, 0x7F)+byte_range(0xC2, 0xF4)
        self.utf8_trailing_values = byte_range(0x80, 0xBF)
        self.currentfolder = os.path.dirname(os.path.realpath(__file__))

    def file_onefile(self, contenttype=None, size=None):
        """ simple generator a file"""
        if contenttype  is not None or size is not None:
            contenttype, size = random_string(contenttype=contenttype,
                                              size=size)
        else:
            contenttype, size = random_string()
        content = self.string_generator(size, contenttype)
        filename = file_write(content, contenttype, os.getcwd())
        return filename

    def string_onestring(self, contenttype=None, size=None):
        """ generator a string """
        if size is not None:
            size = stringtosize(size)
            if contenttype  is None:
                contenttype = random.choice(STRINGTYPE)
            string_ = self.string_generator(size, contenttype)
        else:
            if contenttype  is not  None:
                contenttype, size = random_string(contenttype=contenttype)
            else:
                contenttype, size = random_string()
            string_ = self.string_generator(size, contenttype)
        return string_

    def string_generator(self, size, contenttype,
                         charset=None, additionalset=None):
        """ Generate string with type and size """
        if contenttype == "regular":
            content = string_generator(size)
        elif contenttype == "unicode":
            content = unicode_generator(size)
        elif contenttype == "utf8":
            content = self._utf8_generator(size)
        elif contenttype == "letter":
            content = letter_generator(size)
        elif contenttype == "limited":
            content = string_generator(size, charset=charset)
        elif contenttype.startswith("chinese"):
            if additionalset is None:
                joinstring = ""
                chinesechar = self._chinese_dict_gene(size,
                                                      setname=contenttype[7:])
            else:
                if "joinstring" in additionalset:
                    joinstring = additionalset['joinstring']
                else:
                    joinstring = ""
                chinesechar = self._chinese_dict_gene(size,
                                                      setname=contenttype[7:],
                                                      setting=additionalset)
            content = joinstring.join(chinesechar)
        else:
            print(contenttype)
        return content

    def _utf8_generator(self, size=1014):
        """ generate utf8 string """
        return "".join(chr(self.__utf8_char()) for i in range(size))

    def __utf8_char(self):
        """ generate indiviaul utf8 character """
        first = random.choice(self.utf8_first_values)
        if first <= 0x7F:
            value = bytes([first])
        elif first <= 0xDF:
            value = bytes([first, random.choice(self.utf8_trailing_values)])
        elif first == 0xE0:
            value = bytes([first,
                           random.choice(byte_range(0xA0, 0xBF)),
                           random.choice(self.utf8_trailing_values)])
        elif first == 0xED:
            value = bytes([first,
                           random.choice(byte_range(0x80, 0x9F)),
                           random.choice(self.utf8_trailing_values)])
        elif first <= 0xEF:
            value = bytes([first,
                           random.choice(self.utf8_trailing_values),
                           random.choice(self.utf8_trailing_values)])
        elif first == 0xF0:
            value = bytes([first,
                           random.choice(byte_range(0x90, 0xBF)),
                           random.choice(self.utf8_trailing_values),
                           random.choice(self.utf8_trailing_values)])
        elif first <= 0xF3:
            value = bytes([first,
                           random.choice(self.utf8_trailing_values),
                           random.choice(self.utf8_trailing_values),
                           random.choice(self.utf8_trailing_values)])
        elif first == 0xF4:
            value = bytes([first,
                           random.choice(byte_range(0x80, 0x8F)),
                           random.choice(self.utf8_trailing_values),
                           random.choice(self.utf8_trailing_values)])
        utf8v = 0
        for i in value:
            utf8v += int(i)
        return utf8v

    def _chinese_generator(self, size=1024):
        """ generate chinese charat """
        pass

    def _chinese_dict_gene(self, size=10, setname="word", setting=None):
        """ generate from predefine dictionary
            https://github.com/pwxcoo/chinese-xinhua/tree/master/data
        """
        if setting is not None:
            pass
        else:
            if setname in ['ci', 'word', 'idiom', 'xiehouyu']:
                filename = f"{self.currentfolder}/chinese/{setname}.json"
            else:
                print(f"raise an error,setname is {setname}")
            with open(filename, "r", encoding='utf-8') as filehandle:
                cchrs = json.load(filehandle)
            chineseswords = []
            for _ in range(size):
                cword = random.choice(cchrs)
                if setname in ["word", "idiom"]:
                    chineseswords.append(cword['word'])
                elif setname == "ci":
                    chineseswords.append(cword['ci'])
                elif setname == "xiehouyu":
                    chineseswords.append(cword['riddle'])
        return chineseswords

def localtest_funcs():
    """Test individual functions"""
    pass

def localtest_classes():
    """ test local classes"""
#    test Data_Generator
    cins = DataGenerator()
    for _ in STRINGTYPE:
        print(cins.string_generator(contenttype=_, size=100))

def main():
    """ main function for lcoal usage"""
    pass

if __name__ == '__main__':
    main()
