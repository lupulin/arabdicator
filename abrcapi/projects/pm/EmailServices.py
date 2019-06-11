# -*- coding: utf-8 -*-
'''
Created on Jan 28, 2013

@author: Chris Bartos
@file: /Users/topher/Developer/abrcapi/abrcapi/projects/pm/EmailServices.py

'''
from HTMLParser import HTMLParser
from abrcapi.projects.pm.models import Issue, Comment, Project, Resolution, \
    Status, Priority, IssueType
from abrcapi.projects.pm.utils import EmailScraper, unescape, getStaffGroup
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.template.context import Context
from django.template.loader import get_template
from email_reply_parser import EmailReplyParser
from itertools import chain
import email
import re
import string

class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_html(html):
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()

class EmailServices(object):
    
    def __init__(self, emailList=None):
        self._emails = emailList
    
    def parseEmails(self, count, addrs, imap, smtp):
        '''
        '''
        for num in count:
            typ, emailData = imap.fetch(num, '(RFC822)')
            msg = email.message_from_string(emailData[0][1])
            fromEmail = msg.get("From")
            userEmail = self._cleanFromEmailAddress(fromEmail)
            msg.replace_header("From", userEmail)
            subj = msg.get("Subject")
            commentText = msg.get("Body")
            body, subject = self.createEmailToCentralServer(subj, unescape(commentText), userEmail)
            msg.replace_header("Subject", subject)
            
            for emailAddr in addrs:
                msg.replace_header('To', emailAddr)
                smtp.sendmail(userEmail, [emailAddr], msg.as_string())
            
            imap.store(num, '+FLAGS', '\\Deleted')
        imap.expunge()
    
    def notEmpty(self, x):
        return x != ""
    
    def getListOfEmails(self, issueId, justStaff=False):
        issue = Issue.objects.get(pk=issueId)
        if justStaff:
            projLead = issue.project.lead if issue.project.lead.groups.filter(name="pm_staff") else ""
            assignees = issue.assignees.filter(groups__name="pm_staff")
            reporter = issue.reporter if issue.reporter.groups.filter(name="pm_staff") else ""
            watchers = issue.watchers.filter(groups__name="pm_staff")
        else:
            projLead = issue.project.lead
            assignees = issue.assignees.all()
            reporter = issue.reporter
            watchers = issue.watchers.all()
        userList = filter(self.notEmpty, list(chain(assignees, [reporter], [projLead], watchers)))
        return set([x.email for x in userList])
            
    def findProjectIssueInformation(self, subj):
        '''
        {{ Project Key }}-{{ Issue ID }}
        
        returns boolean -- True: Issue already exists, create a comment.
                           False: Issue doesn't exist, create an issue.
        '''
        match, subject = self._getMatchFromSubject(subj)
        if match is not None:
            return (True, match.group(1), subject)
        else:
            return (False, match, subject)
    
    def findClosestProject(self, email):
        projects = Project.objects.all()
        
        closestProject = projects[0]
        closestAverage = self._parseEmailForSearchWords(email, self._getSearchWords(closestProject.searchword_set.all()))
        projects = projects[1:]
        
        for project in projects:
            search_words = self._getSearchWords(project.searchword_set.all())
            average = self._parseEmailForSearchWords(email, search_words)
            
            # If average of the current search words is greater than
            # the closest average, change the closest Project to current
            # project.
            if average > closestAverage:
                closestAverage = average
                closestProject = project
        
        # if closest average is 0.0 even after checking every set of 
        # search words, the issue should be sent to Miscellaneous
        if closestAverage == 0.0:
            try:
                misc = Project.objects.get(key="MISC")
                return misc
            except:
                lead = User.objects.all()[0]
                misc = Project(key="MISC", lead=lead, name="Miscellaneous")
                misc.save()
                return misc
        
        return closestProject
    
    def createIssue(self, proj, issue, description, description_html, reporter, attachments=[]):
        try:
            resolution = Resolution.objects.get(pk=6)
            status = Status.objects.get(pk=1)
            priority = Priority.objects.get(pk=4)
            issuetype = IssueType.objects.get(pk=4)
            issue = Issue(project=proj, 
                          reporter=reporter, 
                          name=issue, 
                          description=description, 
                          description_html=description_html,
                          resolution=resolution,
                          status=status,
                          priority=priority,
                          type=issuetype )
            issue.save()
            
            # save all the attachments
            for attachment in attachments:
                issue.attachment_set.create(name=attachment)
            
            return issue
        except Exception, e:
            print e
            return None
    
    def createComment(self, issueId, comment, commenter, attachments=[]):
        try:
            issue = Issue.objects.get(pk=issueId)
            try:
                print "Attempting to change issue status..."
                inProgress = Status.objects.get(pk=2)
                if issue.status.name != inProgress:
                    issue.status = inProgress
                    issue.save()
            except:
                print "issue could not be changed to 'In Progress'..."
            newComment = Comment(issue=issue, comment=comment, commenter=commenter)
            newComment.save()
            
            # save all the attachments
            for attachment in attachments:
                newComment.issue.attachment_set.create(name=attachment)
                
            return newComment
        except:
            return None
    
    def createEmailToCentralServer(self, subj, body, html, email, attachments=[]):
        '''
        Make an email with the project key and issue id and subj and body
        
        return it.
        '''
        exists, match, subj = self.findProjectIssueInformation(subj)
        description = ""
        try:
            description = body[0].get_payload()
        except:
            description = body
        
        description_html = html
        issue = None
        thisUser = None

        try:
            thisUser = User.objects.get(email=email)
        except:
            thisUser = User(username=email, first_name='Anonymous', last_name='User', email=email)
            thisUser.set_unusable_password()
            thisUser.save()
        
        try:
            if exists:
                print "Issue exists, attempting to create a comment"
                
                # This strips the HTML twice. Once, to remove the HTML before stripping the reply
                # email and once more incase there is HTML in the reply email...
                if description is None or description == "":
                    description = strip_html(description_html)
                description = EmailReplyParser.parse_reply(description).strip()
                comment = self.createComment(match, strip_html(description).strip(), thisUser, attachments)
                issue = comment.issue
            else:
                print "Issue doesn't exist, attempting to create an issue"
                proj = self.findClosestProject(subj+description)
                print proj.key, subj, description, thisUser
                issue = self.createIssue(proj, subj, description, description_html, thisUser, attachments)
        except Exception, e:
            print e
        # develop the email and send it.
        if issue is None:
            print "Issue is none, this is clearly an error"
    
    def createSubject(self, issueId):
        '''
        Create a subject from a template.
        '''
        issue = Issue.objects.get(pk=issueId)
        project = issue.project
        tmplt = get_template("email/subject.txt")
        data = {
            'project': project,
            'issue': issue
        }
        d = Context(data)
        return tmplt.render(d)
    
    def createBody(self, data):
        '''
        Create a body from a comment or issue
        '''
        try:
            return data.description
        except:
            return None
        
    def sendEmailWithAttachment(self, send_from, send_to, subject, body, files=[]):
        msg = EmailMessage(subject, body, send_from, [send_to])
        for f in files:
            msg.attach_file(f)
        msg.send()
    
###################
# private methods #
###################
    
    def _getSearchWords(self, searchwords):
        return [x.word for x in searchwords]
    
    def _cleanFromEmailAddress(self, addr):
        s = EmailScraper()
        userEmail = s.collectAllEmail(addr)
        return userEmail[0]
    
    def _parseEmailForSearchWords(self, email, searchWords):
        """
        Parse the entire email, including the subject (minus the project info) and create a word array with
        all the email words.
        
        Create a binary array of whether or not the search word is a word in the email. map() count all the
        1's and make an percent average. Whatever set of search words have a higher percentage, it's a good
        chance that that project is the project the email should be made into an issue.
        """
        searchWords = [x.lower().decode('utf-8', 'ignore') for x in searchWords]  # make everything lowercase
        words = self._removePunctuationGetWordArray(email)              # remove punctuation
        found = [1 if x.lower().decode('utf-8', 'ignore') in searchWords else 0 for x in words]   # create binary array. Word found = 1, Not found = 0
        numberFound = reduce(lambda a,b: a+b, found)                    # add all the 1s
        totalWords = len(words) * 1.0                                   # add decimal place.
        return (numberFound / totalWords)                               # get an average of search words
    
    def _removePunctuationGetWordArray(self, s):
        return (re.sub('[%s]' % re.escape(string.punctuation), '', s.lower())).split()
    
    def _getMatchFromSubject(self, subject):
        pattern = re.compile(r"\(\w+-(\w+)\)")
        match = re.search(pattern, subject)
        
        # Create a new subject without the prefixes
        subject = self._cleanSubject(subject, match)
        return (match, subject)
        
    def _cleanSubject(self, subj, match):
        subj = subj.replace('\n', '').replace('\r', '')
        try:
            return subj[match.end()+2:].strip()
        except: 
            return subj
        
def getRcptEmails(issue, projLead=True, reporter=True, watchers=True, assignees=True, internalOnly=False):
    emails = []
    if projLead:
        emails += [issue.project.lead.email]
    if reporter:
        if internalOnly:
            if getStaffGroup() in issue.reporter.groups.all():
                emails += [issue.reporter.email]
        else:
            emails += [issue.reporter.email]
    if watchers:
        try:
            emails += [watcher.email for watcher in issue.watchers.all()]
        except:
            pass
    if assignees:
        try:
            emails += [assignee.email for assignee in issue.assignee.all()]
        except:
            pass
    return emails

class EmailSender(object):
    """
    EmailSender 
    -----------
    is our business logic class that will determine
    if an email should be sent or not based on the item that was
    saved in the database and whether it is internal or external 
    correspondence.
    """
    def __init__(self):
        pass
    
    def setupEmailBroadcast(self, item, staff_only=False):
        """
        Calculates and returns the following:
        
        1) Dict of emails and the template for the body
        2) Get the subject for the email
        """
        pass
    
emailSender = EmailSender()
    
