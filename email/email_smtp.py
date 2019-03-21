"""
 This module is used to do Email SMTP related operations
"""
__all__ = ["SmtpOps",
           "folder_report", "folder_getfiles", "file2attach", "file_splitgroup"]

# import default system library
import smtplib
import os


# import 3rd party library
import glob2

# import shared library
from base0.baselibs import Appbasic
from base0.baselibs import timecounter as tc
from base0.exception import AppException
from base0.data.data_gen import DataGenerator
from base0.email.email_builder import webfile2mimebody, email_simple_builder
from base0.email.email_builder import email_mime_builder, email_mime_builder_attach
from base0.constant import WEBFILENAME


def folder_report(filegroup, filesizes,
                  emaillist, group, atta):
    """create folder report """
    totalsize = 0
    for filesize in filesizes:
        totalsize += filesize[1]
    if atta:
        reportstring = f"""
There are total {len(filegroup)+1} emails sent out.
Total {len(filesizes)} files attached as attachment.
Total file size is {totalsize}"""
    else:
        reportstring = f"""
There are total {len(filegroup)+1} emails sent out.
Total {len(filesizes)} files attached as html.
Total file size is {totalsize}"""

    for entry in emaillist:
        filesizestring = ""
        if group != 1:
            for filename in entry[1]:
                filesizestring = f"""
{filesizestring}{filename[0]}\t\t{filename[1]}"""
        else:
            filesizestring = f"""
{filesizestring}{entry[1][0][0]}\t\t{entry[1][0][1]}"""
        linestring = f"""
{entry[0]}
{filesizestring}"""
        reportstring += linestring
    return reportstring

def folder_getfiles(folder, extlist):
    """ get file from folder """
    if folder[-1] == "\\" or folder[-1] == "/":
        folder = folder[:-1]
    filelist = []
    if extlist is None:
        filelist = glob2.glob(f"{folder}/**/*.*")
    else:
        for ext in extlist:
            files = glob2.glob(f"{folder}/**/*.{ext}")
            filelist += files
    return  filelist

def file2attach(files):
    """ attach file"""
    mimestring = "Python script to send email in folder\n"
    filesize = []
    for filename in files:
        size = os.stat(filename).st_size
        mimestring += f"{filename}\t\t{size}\n"
        filesize.append((filename, size))
    mimecontent = [(mimestring, "plain")]
    return mimecontent, filesize

def file_splitgroup(filelist, group):
    """ separate the files in groups"""
    count = len(filelist)/group
    left = len(filelist)%group

    filegroup = []
    for i in range(count):
        number_start = i*group
        number_end = (i+1)*group
        filegroup.append(filelist[number_start:number_end])
    if left != 0:
        filegroup.append(filelist[count*group:])
    return filegroup

class SmtpOps(Appbasic):
    """ basic library for smtp related operation
        * smtp through SSL connection
         http://www.blog.pythonlibrary.org/2013/06/26/python-102-how-to-send-an-email-using-smtplib-email/
        Issues:
        1. when send email body in utf8 or unicde, size is not match, mabye dbcs,
        like size set to 10k, email is 20k
    """

    def __init__(self, servername, username=None, password=None):
        """ initial smtp objects """
        Appbasic.__init__(self, self.__class__.__name__)
        self.server = servername
        self.from_ = "anyone@anywhere.com"
        self.username = username
        self.password = password
        self.ptime = tc()

    def email_ts1k(self, email_):
        """send email with 1k size with time stamp"""
        timestamp = str(tc())
        email_['subject'] = f"TS::{timestamp}"
        email_['body'] = f"Email is generated from Python script.\nTime stamp is {timestamp}"
        if 'fromaddr' in email_:
            email_['fromaddr'] = self.from_
        emails, msg = email_simple_builder(email_)
        self._smtp_send(msg, emails, email_['fromaddr'])
        email_['emails'] = emails
        email_['ts'] = timestamp
        return email_

    def email_mimeemail(self, email_,
                        filenames=None, timestampset=True):
        """send mime email """
        timestamp = str(tc())
        if 'fromaddr' not in email_:
            email_['fromaddr'] = self.from_

        if "subject" not in email_:
            email_['subject'] = f"Email: one email at TS::{timestamp}"

        if "unicode" not in email_:
            email_['unicode'] = False

        if filenames is not None:
            emails, msg, timestamp = email_mime_builder_attach(email_,
                                                               filenames=filenames,
                                                               timestampset=timestampset)
        else:
            emails, msg, timestamp = email_mime_builder(email_,
                                                        timestampset=timestampset)
        self._smtp_send(msg.as_string(), emails, email_['fromaddr'])
        email_['emails'] = emails
        email_['ts'] = timestamp
        return email_

    def email_folder2email(self, email_,
                           folder, extlist=None, group=5):
        """ send files in a folder to email"""
        filegroup = file_splitgroup(folder_getfiles(folder, extlist), group)
        filesizes = []
        emaillist = []
        for filename in filegroup:
            timestamp = str(tc())
            if not email_['attachment']:
                email_['body'], filesize = webfile2mimebody(filename, WEBFILENAME)
                email_['subject'] = f"Email: Folder {folder} convert to HTML at {timestamp}"
                filenames = None
            else:
                email_['body'], filesize = file2attach(filename)
                email_['subject'] = f"Email: Folder {folder} convert to attachment at {timestamp}"
                filenames = filename
            filesizes += filesize
            if len(filesize) != len(filename):
                raise AppException(self.appname, 102, "file size is not match")
            emaillist.append((email_['subject'], filesize))
            self.email_mimeemail(email_, filenames=filenames)

        reportstring = folder_report(filegroup, filesizes, emaillist,
                                     group, email_['attachment'])
        if email_['attachment']:
            email_['subject'] = f"Email: Folder {folder} convert to attachment Report"
        else:
            email_['subject'] = f"Email: Folder {folder} convert to HTML Report"
        email_['body'] = [(reportstring, "plain")]
        self.email_mimeemail(email_)

    def email_oneemail(self, email_,
                       size=None, keepfile=False, timestampset=True):
        """ send single one email"""
        dgins = DataGenerator()
        if "atta" not in email_:
            atta = False
        else:
            atta = email_['attachment']

        if 'contenttype' not in email_:
            email_['contenttype'] = "regular"

        if "unicode" not in email_:
            email_['unicode'] = False

        if atta is None:
            filename = dgins.file_onefile(contenttype=email_['contenttype'],
                                          size=size)
            email_['body'] = [("Email with attachment from python script", "plain")]
            filenames = [filename]
        else:
            string = dgins.string_onestring(contenttype=email_['contenttype'],
                                            size=size)
            if email_['contenttype'] == "regular":
                email_['body'] = [(string, "plain")]
            else:
                email_['body'] = [(string, "plain", "utf-8")]
            filenames = None
        emailinfo = self.email_mimeemail(email_,
                                         filenames=filenames,
                                         timestampset=timestampset)
        if atta and not keepfile:
            os.remove(filename)
        return emailinfo

    def _smtp_send(self, msg, toaddrs, fromaddr):
        """ send email with smtp"""
        smtp_ins = smtplib.SMTP(self.server)
        retcode = smtp_ins.sendmail(fromaddr, toaddrs, msg)
        if retcode != {}:
            raise AppException(self.appname, 101, retcode)
        return retcode

def localtest_funcs():
    """Test individaul functions"""
    pass

def localtest_classes():
    """ Test local classes """
    S_ins = SmtpOps("maine64.devemc.commvault.com")
    email="travelalone@devemc.commvault.com"
    D_ins = DG()
    for i in range(50):
        subject = D_ins.string_generator(size=3,contenttype="chineseci")
        print(subject,i)
        email_ = {"toaddrs": email,
                  "subject": subject,
                  'contenttype' : "chineseword", 
                  "unicode": True}
        S_ins.email_oneemail(email_,
                             size="200".format(random.randint(1300,2500)))
        S_ins.email_ts1k(email_)

def main():
    """ main function for local usage"""
    pass

if __name__ == '__main__':
    main()
