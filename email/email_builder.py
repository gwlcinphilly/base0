"""
This module is use to build a email
"""
__all__ = ["recipient_builder", "webfile2mimebody", "email_mime_attch_file",
           "email_simple_builder", "email_mime_builder_attach",
           "email_mime_builder"]

# import default system library
from email.base64mime import body_encode
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

# import 3rd party library

# import shared library
from base0.baselibs import timecounter as tc

def recipient_builder(toaddrs):
    """build email recipient"""
    tostring = ""
    rdict = {"To":[], "CC":[], "BCC":[]}
    toaddrs = toaddrs.split(';')
    for emailentry in toaddrs:
        if emailentry.startswith("CC"):
            rdict['CC'] = emailentry[3:].split(",")
        elif emailentry.startswith("BCC"):
            rdict['BCC'] = emailentry[4:].split(",")
        else:
            rdict['To'].append(emailentry)

    emails = []
    if rdict['To'] != []:
        recipientstring = f"To: {', '.join(rdict['To'])}\r\n"
        tostring = tostring+recipientstring
        emails = emails+rdict['To']
    if rdict['CC'] != []:
        recipientstring = f"CC: {', '.join(rdict['CC'])}\r\n"
        tostring = tostring+recipientstring
        emails = emails+rdict['CC']
    if rdict['BCC'] != []:
        recipientstring = f"BCC: {', '.join(rdict['BCC'])}\r\n"
        tostring = tostring+recipientstring
        emails = emails+rdict['BCC']
    return emails, tostring, rdict

def webfile2mimebody(files, extlist):
    """ get web file to mime body"""
    mimecontent = []
    filesize = []
    for filename in files:
        if filename.split('.')[-1].lower() in extlist:
            with open(filename, 'r') as filehandle:
                filecontent = filehandle.read()
            fileline = f"""
{'*'*40}
{filename}
{'*'*40}"""
            mimecontent.append((fileline, "plain"))
            mimecontent.append((filecontent, 'html'))
            filesize.append((filename, len(filecontent)))
    return mimecontent, filesize

def email_simple_builder(email_):
    """ build simple email """
    msgstring = ""
    timestamp = str(tc())
    fromaddr = email_['fromaddr']
    toaddrs = email_['toaddrs']
    subject = email_['subject']
    body = email_['body']
    if  subject is not None:
        if "TS::" in subject:
            msgstring = f"Subject:{subject}\n"
        else:
            msgstring = f"Subject:{subject} TS::{timestamp}\n"
    else:
        msgstring = f"TS::{timestamp}\n"
    if body is not None:
        msgstring = f"{msgstring}\n{body}"
    emails, tostring, _ = recipient_builder(toaddrs)
    msg = (f"From: {fromaddr}\r\n{tostring}{msgstring}")
    return emails, msg

def email_mime_attch_file(filename, unicode):
    """check attachment file
    # Guess the content type based on the file's extension.  Encoding
    # will be ignored, although we should check for simple things like
    # gzip'd or compressed files.
    """
    ctype, encoding = mimetypes.guess_type(filename)
    if ctype is None or encoding is not None:
# No guess could be made, or the file is encoded (compressed), so
# use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype not in ['text', 'image', 'audio', 'application']:
        print('message or error for unknow type file')
    if unicode:
        with open(filename, 'rb') as filehandle:
            attachment = MIMEText(filehandle.read(), 'html', 'UTF-8')
    else:
        if maintype == 'text':
            with open(filename, 'rb') as filehandle:
    # Note: we should handle calculating the charset
                attachment = MIMEText(filehandle.read(),
                                      _subtype=subtype,
                                      _charset=body_encode)
        elif maintype == 'image':
            with open(filename, 'rb') as filehandle:
                attachment = MIMEImage(filehandle.read(),
                                       _subtype=subtype)
        elif maintype == 'audio':
            with open(filename, 'rb') as filehandle:
                attachment = MIMEAudio(filehandle.read(),
                                       _subtype=subtype)
        elif maintype == 'application':
            with open(filename, 'rb') as filehandle:
                attachment = MIMEApplication(filehandle.read(),
                                             _subtype=subtype)
        else:
            with open(filename, 'rb') as filehandle:
                attachment = MIMEBase(filehandle.read(),
                                      subtype)
    # Encode the payload using Base64
            encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment",
                          filename=filename)
    return attachment

def email_mime_builder_attach(email_, filenames=None,
                              timestampset=True):
    """ build email bbody with attachment """
    msg = MIMEMultipart()
    msg['From'] = email_['fromaddr']
    msg['Subject'] = email_['subject']
    emails, _, rdict = recipient_builder(email_['toaddrs'])
    msg['To'] = ', '.join(rdict['To'])
    msg['CC'] = ', '.join(rdict['CC'])
    msg['BCC'] = ', '.join(rdict['BCC'])

    if email_['subject'] is not  None:
        if "TS::" in email_['subject']:
            timestamp = email_['subject'].split("TS::")[1]
        else:
            timestamp = str(tc())
            if timestampset:
                msg['Subject'] += f" TS::{timestamp}"
    else:
        timestamp = str(tc())
        msg['Subject'] = f"Email:Mime email at TS::{timestamp}"

    if email_['body'] is not  None:
        for entry in email_['body']:
            print(entry)
            text = MIMEText(entry[0], entry[1])
            msg.attach(text)
    else:
        text = MIMEText("This is Mime email from python script", 'plain')
        msg.attach(text)

    if "unicode" not in email_:
        unicode = False
    else:
        unicode = email_['unicode']
    if filenames is not None:
        for filename in filenames:
            attachment = email_mime_attch_file(filename, unicode)
            msg.attach(attachment)
    return emails, msg, timestamp

def email_mime_builder(email_, timestampset=True):
    """ email build mime body"""
    msg = MIMEMultipart()
    msg['From'] = email_['fromaddr']
    emails, _, rdict = recipient_builder(email_['toaddrs'])
    msg['To'] = ', '.join(rdict['To'])
    msg['CC'] = ', '.join(rdict['CC'])
    msg['BCC'] = ', '.join(rdict['BCC'])
    subject = email_['subject']
    body = email_['body']

    if subject is not None:
        if "TS::" in subject:
            msg['Subject'] = subject
            timestamp = subject.split("TS::")[1]
        else:
            timestamp = str(tc())
            if timestampset:
                msg['Subject'] = f"{subject} TS::{timestamp}"
            else:
                msg['Subject'] = subject
    else:
        timestamp = str(tc())
        msg['Subject'] = f"Email:Mime email at TS::{timestamp}"
    if body is not None:
        if isinstance(body, str):
            text = MIMEText(body, 'plain')
            msg.attach(text)
        else:
            for entry in body:
                text = MIMEText(entry[0], entry[1])
                msg.attach(text)
    else:
        pass
    return emails, msg, timestamp
