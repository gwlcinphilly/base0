"""
This library is use to analyst log
"""
__all__ = []


from base0.baselibs import Appbasic

class LogAnalyst(Appbasic):
    """ Class to analyst Commvault log files """

    def __init__(self, logfile, logpattern):
        Appbasic.__init__(self, self.__class__.__name__)
        self.filename = logfile
        with open(self.filename, 'r')as \
        filehandleobj: filecontent = filehandleobj.read()
        self.content = [fileline for fileline in \
                        filecontent.split('\n') if fileline != ""]
        self.contlen = len(self.content)
        self.format_pat = logpattern['pattern']
        self.format_seq = logpattern['sequence']
        self.format_list = [entry[0] for entry in self.format_seq]
        self.contentdict = []
        return None

    def _log_header(self):
        pass

    def _log_header_remove(self):
        pass

    def _format_generator(self):
        patternstring = "^"
        for entry in self.format_seq:
            patt = entry[0]
            sepa = entry[1]
            entry_string = '(?P<%s>%s)%s' % (patt,
                                             self.format_pat[patt],
                                             sepa)
            patternstring = "%s%s" % (patternstring, entry_string)
        return patternstring

    def loglinesplit(self):
        """split ech log line to dict"""
        loglinelist = []
        for i in range(self.contlen-1):
            patternstring = self._format_generator()
            matchresult = re.match(r'%s' % patternstring, self.content[i])
            if matchresult:
                loglined = matchresult.groupdict()
                for entry in self.format_list:
                    loglined[entry] = matchresult.groupdict()[entry]
                loglined['content'] = self.content[i][matchresult.end():]
                self.contentdict.append(loglined)
                loglinelist.append(i)
        count = -1
        for i in range(self.contlen-1):
            if i in loglinelist:
                count += 1
            else:
                self.contentdict[count]['content'] = "%s\n%s" %\
                 (self.contentdict[count]['content'], self.content[i])
        return None

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

