"""
This module is used to check python script base don pylint.

"""
__all__ = ['PylintCheck']
# import default system library

# import 3rd party library
from pylint import lint
from pylint.reporters.text import TextReporter

# import shared library
from base0.baselibs import Appbasic
from base0.baselibs import timecounter as tc
from base0.string.string_process import stringclean, stringgroup
from base0.constant import PYLINTMESSAGE, PYLINTCHECKVARS

import inspect 
# inpsect should be used to check the code and analyst 
def getimportlist(filename):
    """Get all import library in the script"""
    from modulefinder import ModuleFinder
    findmodules = ModuleFinder()
    libsname = findmodules.run_script(filename)
    return libsname

class PylintCheck(Appbasic):
    """Using pylint to check scirpt and evaluate the code quality"""
    def __init__(self, scriptname, path=None):
        Appbasic.__init__(self,self.__class__.__name__)        
        if path is None:
            if scriptname[-3:] in ['.py', ".PY"]:
                self.script = scriptname
            else:
                self.script = f"{scriptname}.py"
        self.result = []
        self.modulename = ""
        self.rate = 0.0
        self.pre_rate = 0.0
        return None

    def run(self):
        """run lint to analyst the script """
        args = ["-r", "n"]
        lint.Run([self.script]+args, reporter=TextReporter(pylint_output), exit=False)
        self.result = stringclean(pylint_output.read())
        return None

    def analyst(self):
        """analyst pylint result"""
        resultgroup = self._result_split()
        return resultgroup

    def _result_group(self, save=True):
        """analyst the result, group the report """
        resultgroup = stringgroup(self.result[1:-2], PYLINTMESSAGE, {})
        if save or self.rate != 10.0:
            self._result_save(resultgroup)
        return resultgroup

    def _result_split(self):
        """analyst the result, separate the result"""
        strsplitres = self.result[0].split("*************")
        if len(strsplitres) == 2:
            self.modulename = strsplitres[1].strip().split("Module ")[1]
        strsplitres = self.result[-1].split("Your code has been rated at ")
        if len(strsplitres) == 2:
            self.rate = float(strsplitres[1].strip().split("/")[0])
            try:
                self.pre_rate = float(strsplitres[1].strip()\
                                  .split("previous run: ")[1].split("/")[0])
            except IndexError:
                self.log.debug("There is not prior \
                                record for module %s", self.modulename)
        if self.modulename == "":
            resultgroup = self._result_group(save=False)
        else:
            resultgroup = self._result_group()
        return resultgroup

    def _result_save(self, resultgroup):
        """save result to local files"""
        filename = f'data/{self.modulename}_{tc(timeformat="filename")}_{self.rate}.txt'
        filehandleins = open(filename, "a")
        datastring = ""
        for varname in PYLINTCHECKVARS:
            datastring += "%s\t:%s\n" % (varname, getattr(self, varname))
        datastring += "\n\n"
        for keyword in PYLINTMESSAGE:
            if resultgroup[keyword] != []:
                datastring += "%s :%s\n%s\n\n" % (keyword,
                                                  len(resultgroup[keyword]),
                                                  "\n".join(resultgroup[keyword]))
        datastring += "No grouped lines: %s\n" % len(resultgroup['nogrouped'])
        datastring += "\n".join(resultgroup['nogrouped'])
        filehandleins.write(datastring)
        filehandleins.close()
        return None

    def _result_load(self):
        """load saved result from local files"""
        pass

    def _result_compare(self):
        """compare existing results"""
        pass

class PythonCodeAnalyst(Appbasic):
    """This is self defined code analyst for pythons cript """
    
    def __init__(self, pythonfile):
        """ read the python script"""
        self.filename = pythonfile
        with open(self.filename,'r') as filehandle:
            self.content = filehandle.read()
        self.content_lines = []
        self.content_makers = {}
        return None
    
    def content_clean(self, comment=False):
        """ clean empty lines and comment """
        for line in self.content.splitlines():
            if line.strip() not in ["",None]:
                self.content_lines.append(line.strip())
        
        return None
    
    def content_separate(self):
        """ seperate python code with special keyword"""
        switchlist = ["from", "import", "class", "def", '"""']
        switchresult_mapper = {"from"   : "import_from",
                               "import" : "import_import",
                               "class"  : "class",
                               "def"    : "function",
                               '"""'    : "comment"}
        
#        SwitchCase(switchlist,"startswith",
#                                self.content_lines,
#                                switchresult_mapper)
        
#        self.content_makers = SwitchCase.checkcontent()
        return self.content_makers
    
    def content_analyst(self):
        self.content_clean()
        markers = self.content_separate()
        return markers
    
    
def localtest(modulename=None):
    """ test functions/classes in this library"""
    if modulename is None:
        lintins = PylintCheck(__file__)
    else:
        lintins = PylintCheck(modulename)
    lintins.run()
    lintins.analyst()
    return lintins.rate

def main():
    """ main function for lcoal usage"""
    pass

if __name__ == '__main__':
    main()
