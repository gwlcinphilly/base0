"""
This library is use to analyst log
"""
__all__ = []
import re
import os
import json

from base0.baselibs import Appbasic, get_log

def filename_gen(keyname, ext, savetofile, path):
    """ generate result file name based on input
        keyname    : str    the main string of the filename
        ext        : str    the file extension of file
        savetofile : Boolean/str    if the value is Boolean, decide to save fiel or not
                                    if the value is str, will append string to keyname
        path       : str    the path to save the file
    """
    if isinstance(savetofile, str):
        basefilename = f"{keyname}_{savetofile}.{ext}"
    else:
        basefilename = f"{keyname}.{ext}"

    if path:
        filename = os.path.join(path, basefilename)
    else:
        filename = basefilename
    return filename

def file_save(keyname, ext, content, savetofile, path):
    filename = filename_gen(keyname, ext, savetofile, path)
    with open(filename, 'w', encoding='utf-8') as filehandle:
        if ext == "json":
            json.dump(content, filehandle)
        elif ext == "log":
            for _ in content:
                filehandle.write(_+"\n")
    return filename

RE_PATTERN_NUMBER = "\d+"
RE_PATTERN_ALL = ".+"

 
def re_generator(patternlist):
    re_string = ""
    for _ in patternlist:
        if isinstance(_, str):
            re_string +=_
        elif isinstance(_, dict):
            match_keys = list(_.keys())
            if len(match_keys) >1:
                match_sepa = _['spea']
                match_key = [mkey for mkey in match_keys if mkey != "sepa"]
            else:
                match_sepa = ""
                match_key = list(_.keys())[0]
            match_pattern = _[match_key]
            pattern_string = locals[f"RE_PATTERN_{match_pattern.upper()}"]

            if match_key == "RE_MATCH":
                re_match =  pattern_string
            else:
                re_match = f"(?P<{match_key}>{pattern_string}){match_sepa}"
            re_string +=re_match
    return re_string

class LogAnalyst(Appbasic):
    """ Class to analyst Commvault log files """

    def __init__(self, logfile, logpattern={}):
        Appbasic.__init__(self, self.__class__.__name__)
        self.log = get_log()
        self.filename = logfile
        self.logpattern = logpattern
        self.contentdict = []

    def _log_header(self):
        pass

    def _log_header_remove(self):
        pass

    def _format_generator(self):
        format_pat = self.logpattern['pattern']
        format_seq = self.logpattern['sequence']
        format_list = [entry[0] for entry in format_seq]
        patternstring = "^"
        for entry in format_seq:
            patt = entry[0]
            sepa = entry[1]
            entry_string = '(?P<%s>%s)%s' % (patt,
                                             format_pat[patt],
                                             sepa)
            patternstring = "%s%s" % (patternstring, entry_string)
        return format_list, patternstring

    def _file_open(self, cleanlines=False):
        """open the log file"""
        with open(self.filename, 'r', encoding='utf-8', errors="ignore") as filehandleobj:
            filecontent = filehandleobj.readlines()
        if cleanlines:
            cleanlines = [_ for _ in filecontent if _.strip() not in [""]]
        else:
            cleanlines = []
        return filecontent, cleanlines

    def loglinesplit(self):
        """split ech log line to dict"""
        loglinelist = []
        content = self._file_open()
        content_len = len(content)
        for i in range(content_len-1):
            format_list, patternstring = self._format_generator()
            matchresult = re.match(r'%s' % patternstring, content[i])
            if matchresult:
                loglined = matchresult.groupdict()
                for entry in format_list:
                    loglined[entry] = matchresult.groupdict()[entry]
                loglined['content'] = content[i][matchresult.end():]
                self.contentdict.append(loglined)
                loglinelist.append(i)
        count = -1
        for i in range(content_len-1):
            if i in loglinelist:
                count += 1
            else:
                self.contentdict[count]['content'] = "%s\n%s" %\
                 (self.contentdict[count]['content'], content[i])

    def log_load_content(self):
        """ laod content from the logf ile"""
        content, cleanlines = self._file_open()
        return content, cleanlines

    def log_job(self, jobid):
        """filter based on job id"""
        joblog = [entry for entry in \
                  self.contentdict if entry['jobid'] == jobid]
        return joblog

    def log_keyword(self, keyword, contentd=None):
        """filter keyworkd lines"""
        if contentd is None: contentd = self.contentdict # pylint: disable=C0321
        klog = [entry for entry in contentd if keyword in entry['content']]
        return klog

    def log_not_keyword(self, keyword, contentd=None):
        """filter not keyword content"""
        if contentd is None: contentd = self.contentdict # pylint: disable=C0321
        klog = [entry for entry in \
                contentd if keyword not in entry['content']]
        return klog

    def log_list_content_filter(self, listdicts, keyfield, filtercontent):
        """ filter particular content line form the list
            list_ins    :     list    data of log lines, each item is a dict
            keyfield    :     str    dict key name to filter
            filtercontent    : list    a list of content to filter out
        """
        self.log.debug("There are total %s lines", len(listdicts))
        goodcontent = []
        for _ in listdicts:
            if not self.log_line_filter(_[keyfield], filtercontent):
                goodcontent.append(_)
            else:
                self.log.debug("skip the line,%s", _[keyfield]) 
#        goodcontent = [_ for _ in listdicts if _[keyfield] not in filtercontent]
        self.log.debug("There are total %s good lines", len(goodcontent))
        return goodcontent
    
    def log_line_filter(self, line, filtercontent):
        """ check if the line match correct content in the content
        Return:
            Boolean    If found match in the content list, return True
        """
        match_ = False
        for _ in filtercontent:
            if isinstance(_, str):
                if _ in line:
                    match_ = True
                    break 
            elif isinstance(_, list):
                if _[0] in line:
                    match_ = True
                    break
        return match_
    
    def log_list_zone_match(self, listdicts, zone_pattern, keyfield="content"):
        """ split the log with zone based on pattern
        Args:
            listdicts    list    logline dict list 
            zone_pattern    dict    zone match pattern
                        totallines    int    totallines to match
                        keylinescount int    total key line to count 
                        pattern_pdict list   match pattern return 
                        pattern_zone  list   match pattern list one by one, 
                                             this could be re match pattern,
                                             or int to skip unrelated lines
            keyfield    str    the dict field to check, default is content
        Return:
            pzoneresult    dict return matched zones 
                archorlist    list    matched zone started line archor 
                zones        list    matched zone lines
                returndict    list    matched match pattern return list
        """
        zonelines = zone_pattern['totallines']
        keyelementcount = zone_pattern['keylinescount']
        p_plist = zone_pattern['pattern_pdict']
        p_zone = zone_pattern['pattern_zone']
        initial_pattern = zone_pattern['pattern_zone'][0]        
        p0_archorlist = []
        pzones = []
        returndictlist = []
        for cur in range(len(listdicts)):
            linezone = []
            match_ = re.match(initial_pattern, listdicts[cur][keyfield])
            # find the first match
            if match_:
                returndict = {}
                p0_archorlist.append(cur)
                linezone.append(listdicts[cur])
                zone_match = 1
                self.log.debug(f"current at line {cur}, the match line is {zone_match}")
                # match required dict variable
                if p_plist[0] is not None:
                    for id_ in p_plist[0]:
                        returndict[id_] = match_.group(id_)
                # continue match following lines based on patterns
                for patt in p_zone[1:]:
                    #    Skip multiples liens based on the patterns
                    self.log.debug(f"current at line {cur}, the match line is {zone_match}, the matching patt is:\n{patt}")
                    if isinstance(patt, int):
                        cur += patt
                        zone_match += 1
                    else:
                        # try to match availalabe pattern
                        cur += 1
                        match_i = re.match(patt, listdicts[cur][keyfield])
                        if match_i:
                            linezone.append(listdicts[cur])
                            if p_plist[zone_match] is not None:
                                for id_ in p_plist[zone_match]:
                                    returndict[id_] = match_i.group(id_)
                            zone_match += 1             
                        else:
                            self.log.debug("next line is not match, not valid zone")
                    self.log.debug(f"current at line {cur}, the match line is {zone_match}")
                # make sure this is full match
                self.log.debug(f"log zone is scanned, there are total {zone_match}. current at line {cur}")
                if zone_match == keyelementcount:
                    pzones.append(linezone)
                    returndictlist.append(returndict)
            cur += 1
        
        pzoneresult = {
            "archorlist" : p0_archorlist,
            "zones"     : pzones,
            "returndict" : returndictlist}
        return pzoneresult
