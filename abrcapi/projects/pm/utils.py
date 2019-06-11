'''
Created on Jan 4, 2013

@author: Chris Bartos - me@chrisbartos.com
@file: /Users/topher/Developer/abrcpm/abrcpm/pm/utils.py

'''
from abrcapi.projects.pm.models import EmailServer, Issue, Comment, Project, \
    Attachment, Status, Resolution, IssueUpdate
from django.contrib.auth.models import User, Group
from django.core.mail.message import EmailMultiAlternatives
from django.template.context import Context
from django.template.loader import get_template
from htmlentitydefs import name2codepoint
import email
import imaplib
import os
import pyclamd
import re
import smtplib

class EmailScraper():
    def __init__(self):
        self.emails = []

    def reset(self):
        self.emails = []

    def collectAllEmail(self, htmlSource):
        "collects all possible email addresses from a string, but still it can miss some addresses"
        #example: t.s@d.com
        email_pattern = re.compile("[-a-zA-Z0-9._]+@[-a-zA-Z0-9_]+.[a-zA-Z0-9_.]+")
        return re.findall(email_pattern, htmlSource)
        
    def collectEmail(self, htmlSource):
        "collects all emails that starts with mailto: in the html source string"
        #example: <a href="mailto:t.s@d.com">
        email_pattern = re.compile("<a\s+href=\"mailto:([a-zA-Z0-9._@]*)\">", re.IGNORECASE)
        self.emails = re.findall(email_pattern, htmlSource)

# for some reason, python 2.5.2 doesn't have this one (apostrophe)
name2codepoint['#39'] = 39

def unescape(s):
    """unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"""
    return re.sub('&(%s);' % '|'.join(name2codepoint),
              lambda m: unichr(name2codepoint[m.group(1)]), s)

def sendTemplateEmail(template, subject, from_user, to_user, model=None, plaintext=True):
    plaintextTemplate = get_template(template)
    contextData = { 'user': to_user }
    if model:
        contextData['data'] = model
    d = Context(contextData)
    from_email = from_user
    text_content = plaintextTemplate.render(d)
    msg = EmailMultiAlternatives(subject, unescape(text_content), from_email, [to_user.email])
    msg.send()

def handle_uploaded_file(f, issue):
    filename = createUniqueFilename(f.file.name)
    abs_path_to_file = '/home/cbartos/public/pm/attachments/'+filename
    with open(abs_path_to_file, 'wb+') as destination:
        if f.multiple_chunks():
            for chunk in f.chunks():
                destination.write(chunk)
        else:
            destination.write(f.read())
        try:
            if checkFileForVirus(str(abs_path_to_file)):
                print "No virus found..."
                attachment = Attachment.objects.create(issue=issue, name=filename)
            else:
                os.remove(abs_path_to_file)
        except Exception, e:
            print e
    

def createUpdateTemplateBody(update, link):
    plaintextTemplate = get_template("email/update_old_issue.txt")
    if update.acting_user.first_name == "Anonymous":
        user = update.acting_user.email
    else:
        user = update.acting_user.first_name +" "+ update.acting_user.last_name
    contextData = { 'update': update, 'user': user, 'link': link }
    d = Context(contextData)
    return unescape(plaintextTemplate.render(d))
    
def createIssueTemplateBody(issue, link):
    plaintextTemplate = get_template("email/created_new_issue.txt")
    if issue.reporter.first_name == "Anonymous":
        user = issue.reporter.email
    else:
        user = issue.reporter.first_name +" "+ issue.reporter.last_name
    contextData = { 'issue': issue, 'user': user, 'link': link }
    d = Context(contextData)
    return unescape(plaintextTemplate.render(d))

def createCommentTemplateBody(comment, link):
    plaintextTemplate = get_template("email/created_new_comment.txt")
    if comment.commenter.first_name == "Anonymous":
        user = comment.commenter.email
    else:
        user = comment.commenter.first_name +" "+ comment.commenter.last_name
    if comment.issue.reporter.first_name == "Anonymous":
        reporter = comment.issue.reporter.email
    else:
        reporter = comment.issue.reporter.first_name +" "+ comment.issue.reporter.last_name
    contextData = { 'comment': comment, 'user': user, 'reporter': reporter, 'link': link }
    d = Context(contextData)
    return unescape(plaintextTemplate.render(d))

def createEventReminderEmail(user, event):
    plaintextTemplate = get_template("email/event_reminder.txt")
    contextData = { 'user': user, 'event': event}
    d = Context(contextData)
    return unescape(plaintextTemplate.render(d))

def getIMAPConnection():
    incoming = EmailServer.objects.get(type="INCOMING")
    try:
        imap = imaplib.IMAP4_SSL(incoming.hostname, int(incoming.port))
    except:
        imap = imaplib.IMAP4_SSL(incoming.hostname)
    imap.login(incoming.username, incoming.password)
    imap.select()
    return imap

def closeIMAP(connection):
    connection.close()

def getSMTPConnection():
    outgoing = EmailServer.objects.get(type="OUTGOING")
    smtp = smtplib.SMTP_SSL(outgoing.hostname, int(outgoing.port))
    smtp.login(outgoing.username, outgoing.password)
    return smtp, outgoing.email

def closeSMTP(connection):
    connection.close()

def getEmailCount(imapConnection, unseen_only=True):
    typ, data = imapConnection.search(None, '(UNSEEN)')
    return data[0].split()

def forwardEmails(count, imap, smtp):
    '''
    get the list of emails and forward them to the list of email
    addresses.
    '''
    # For each email, forward the email to a list of email addresses.
    for num in count:
        typ, emailData = imap.fetch(num, '(RFC822)')
        
        msg = email.message_from_string(emailData[0][1])
        fromEmail = msg.get("From")
        userEmail = cleanFromEmailAddress(fromEmail)
        msg.replace_header("From", userEmail)
        addrs = [x.email for x in User.objects.all()]

        for emailAddr in addrs:
            msg.replace_header("To", emailAddr)
            # For each email that is successfully sent to each email address,
            # delete the email from the  server.
            smtp.sendmail(userEmail, [emailAddr], msg.as_string())
        
        # Move on to the next email until all the emails are processed.
        imap.store(num, '+FLAGS', '\\Deleted')
        
    # Close both the SMTP and the IMAP connections
    imap.expunge()
    
def fullName(user):
    return user.first_name + " " + user.last_name
    
def createSubjectFromData(issue, project, id):
    return "[ABRC HELP]: Commented: "+ project +"-"+id+": "+issue
    
def parseSubjectForIssue(subject, fromEmail, text):
    '''
    Parse the subject for a Issue Key. If none exists, this is an issue
    and should be saved as an issue. If a key does exist, this is a comment
    and should be saved as such for the issue associated with the issue key.
    '''
    match, subject = getMatchFromSubject(subject)
    
    issue = None
    id = None
    projectKey = None
    isIssue = False
    
    reporter = User.objects.get(email=fromEmail)
    
    if match:
        # if match is not None -- get the issue associated and save a comment
        isIssue = True
        id = match.group(1)
    else:
        # if match is None -- save the issue, get the issue name and key
        
        # This is annoying code. Why you can't do something like:
        # proj = Project.objects.get(primary=True) or Project.objects.all()[0] 
        # is beyond me.
        proj = None
        try:
            proj = Project.objects.get(primary=True)
        except:
            proj = Project.objects.all()[0]
        issue = subject
        newIssue = Issue(project=proj, reporter=reporter, name=subject, description=text)
        newIssue.save()
        id = newIssue.pk
        
    projectKey = Issue.objects.get(pk=id).project.key
    return (issue, id, projectKey, isIssue)
    
def getMatchFromSubject(subject):
    pattern = re.compile(r"\w+-(\w+)")
    match = re.search(pattern, subject)
    
    # Create a new subject without the prefixes
    subject = cleanSubject(subject, match)
    return (match, subject)
    
def cleanSubject(subj, match):
    try:
        return subj[match.end()+1:].strip()
    except:
        return subj

def cleanFromEmailAddress(addr):
    try:
        emailCollector = EmailScraper()
        emailAddr = emailCollector.collectAllEmail(addr)[0]
        user = User.objects.filter(email=emailAddr)[0]
        userEmail = '"' + user.first_name + " " + user.last_name + " (ABRCPM)\" <me@chrisbartos.net>"
    except:
        userEmail = "(ABRCPM) <me@chrisbartos.net>"
 
def createUniqueFilename(filename, path='/home/cbartos/public/pm/attachments/'):
    # get the filename prefix & suffix
    try:
        filePre, filePost = filename.rsplit('/', 1)[1].split('.')
    except:
        filePre, filePost = filename.rsplit('.', 1)
        
    # put the path and file name together to get absolute path
    absPath = path + filename
    uniq = 1
    while os.path.exists(absPath):
        filename = '%s_%d.%s' % (filePre, uniq, filePost)
        absPath = path + filename
        uniq += 1
    return filename
        
def getClamd():
    cd = pyclamd.ClamdUnixSocket()
    try:
        cd.ping()
    except pyclamd.ConnectionError:
        cd = pyclamd.ClamdNetworkSocket()
        try:
            cd.ping()
        except pyclamd.ConnectionError:
            raise ValueError("Could not connect to clam")
    return cd
 
def clean_file(contents, filename, cd):
    """
    Saves the file and scans it for virues before it becomes an
    attachment.
    """
    print "Attempting to save a temp file..."
    tmpfile = "/home/cbartos/public/pm/attachments/"+filename
    f = open(tmpfile, 'wb')
    f.write(contents)
    results = cd.scan_file(tmpfile)
    f.close()
    if results is None:
        print "No virus found..."
    else:
        os.remove(tmpfile)
        
def checkFileForVirus(file):
    """
    Assuming file is the name of a file in tmp
    i.e. /tmp/file_name
    
    Have clamd scan the file for viruses. If file comes back from scan as
    None, return True else, something was found return False
    """
    cd = pyclamd.ClamdUnixSocket()
    try:
        cd.ping()
    except pyclamd.ConnectionError:
        # if failed, test for network socket
        cd = pyclamd.ClamdNetworkSocket()
        try:
            cd.ping()
        except pyclamd.ConnectionError:
            raise ValueError("Cound not connect to clamd server is clamd running??")
            return
    if cd.scan_file(file) is None:
        return True
    else:
        return False

def getStaffGroup():
    return Group.objects.get(name="pm_staff")

def createNewIssueUpdate(issue, field, oldstring, newstring, acting_user):
    update = IssueUpdate(issue=issue, field=field, oldstring=oldstring, newstring=newstring, acting_user=acting_user)
    update.save()

class IssueUpdater(object):
    """
    Class that takes care of updating an issue
    """
    
    def __init__(self):
        pass
    
    @staticmethod
    def issueStatusInProgress(self, issue, acting_user):
        old_status = issue.status
        status = Status.objects.get(name="In Progress")
        self.createNewIssueUpdate(issue, "status", old_status.name, status.name, acting_user)
        self._changeIssueStatus(issue, status)
    
    @staticmethod
    def issueStatusFixed(self, issue, acting_user):
        old_status = issue.status
        old_resolution = issue.resolution
        status = Status.objects.get(name="Fixed")
        resolution = Resolution.objects.get(name="Resolved")
        self.createNewIssueUpdate(issue, "status", old_status.name, status.name, acting_user)
        self.createNewIssueUpdate(issue, "resolution", old_resolution.name, resolution.name, acting_user)
        self._changeIssueResolution(issue, resolution)
        self._changeIssueStatus(issue, status)
    
    def _changeIssueStatus(self, issue, status):
        issue.status = status
        issue.save()
        
    def _changeIssueResolution(self, issue, resolution):
        issue.resolution = resolution
        issue.save()