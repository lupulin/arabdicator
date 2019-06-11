'''
Created on Oct 22, 2012

@author: Chris Bartos - me@chrisbartos.com
@file: /Users/topher/Developer/abrcpm/abrcpm/pm/views.py

This is a celery task that will be called every 1 minute.
It will check our INCOMING mail server for any new emails
and it will forward the emails to our staff.

TODO: This will then have to create a new task. The subject
      of the email will determine which project this email
      is apart of.

TODO: Emails will also go to someone who is not 
      ready weighed down by various tasks. It will end up
      being sort of a load balancer to assign tasks.

'''

from BeautifulSoup import BeautifulSoup
from abrcapi.projects.pm.EmailServices import EmailServices
from abrcapi.projects.pm.models import EmailServer, Issue, Comment, IssueUpdate, \
    Event
from abrcapi.projects.pm.utils import getIMAPConnection, getEmailCount, \
    createIssueTemplateBody, createCommentTemplateBody, createUpdateTemplateBody, \
    createEventReminderEmail, getClamd, clean_file, createUniqueFilename
from celery import Celery
from django.contrib.auth.models import User
from django.core.mail import send_mail, mail_admins
import datetime
import email
import re


EMAILS_TO_AVOID = "abrc@osu.edu"

celery = Celery('distributeEmail', broker="amqp://guest@127.0.0.1:5672//")

@celery.task(name="tasks.distributeEmail")
def distributeEmail():
    '''
    gets a list of email addresses and a imap and smtp connection
    and forwards the emails to each person in the list.
    
    Distribute emails every 1 minute
    
    '''
    # The program will open a IMAP connection to our central server.
    imap = getIMAPConnection()
    
    ### The program will search all the email available on the server.
    
    # delete_original is a tag that tells Arabdicator to remove the email from the central email (True) or
    # mark the emails at "UnRead' (False). False is the default.
    delete_original = EmailServer.objects.get(type="INCOMING").delete_original
    emailCount = getEmailCount(imap)
    
    # Class that provides a lot of email services.
    services = EmailServices()
    
    for num in emailCount:
        typ, emailData = imap.fetch(num, '(RFC822)')
        
        msg = email.message_from_string(emailData[0][1])
        # email.utils and email.Utils both work but my IDE doesn't detect the former as being
        # legit. Dumb.
        fromEmail = email.Utils.parseaddr(msg['From'])[1]
        
        if fromEmail in EMAILS_TO_AVOID:
            imap.store(num, '+FLAGS', '\\Seen')
            continue
        
        subj = msg.get("Subject")
        
        imgSrcs=[]
        
        for part in msg.walk():
            content_type = part.get_content_type()
            payload = part.get_payload()
            imageMatch = re.search("image/\w+", content_type)
            if imageMatch is not None:
                encoding = part.get("Content-Transfer-Encoding")
                imgSrc = "data:"+content_type+";"+encoding+","+payload
                imgSrcs.append(imgSrc)
                
        count = 0
        attachments = []
        body = ""
        html = ""
        
        for part in msg.walk():
            print part.get_content_type()
            matchApplication = re.search("application/\w+", part.get_content_type())
            if part.get_content_type() == "text/plain":
                try:
                    body = unicode(
                        part.get_payload(decode=True),
                        part.get_content_charset(),
                        'replace'
                    ).encode('utf8','replace')
                except:
                    body = part.get_payload(decode=True)
                
            elif part.get_content_type() == "text/html":
                htmlPayload = unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8','replace')
                soup = BeautifulSoup(htmlPayload)
                if len(imgSrcs) != 0:
                    for img in soup.findAll('img'):
                        img['src'] = imgSrcs[count]
                        count+=1
                [s.extract() for s in soup(['script', 'iframe', 'head'])]
                html = str(soup)
                imgSrcs = []
                
            elif matchApplication is not None:
                """
                If there are attachments available, run the antivirus on the
                files until they are found to be free from any viruses.
                """
                try:
                    contents = part.get_payload(decode=True)
                    cd = getClamd()
                    filename = createUniqueFilename(part.get_filename())
                    clean_file(contents, filename, cd)
                    attachments.append(filename)
                except Exception, e:
                    message = """
                    Error saving attachments:
                    
                    %s
                    """ % (e)
                    mail_admins("Error: Saving attachments", message=message)
                    print "Error: Something happened probably getting a new filename"
                    print e
        
        try:
            # Add the attachments to the .createEmailToCentralServer function
            # All we need to do is pass the list of attachment filenames. As long as they are
            # saved to the database, we'll know where they are on the server.
            services.createEmailToCentralServer(subj, body, html, fromEmail, attachments)
        except Exception, e:
            print "Oops, something happened parsing emails. Attempting to print out the error message."
            print e
            pass
        
        # Move on to the next email until all the emails are processed.
        if not delete_original:
            imap.store(num, '+FLAGS', '\\Seen')
        else:
            imap.store(num, '+FLAGS', '\\Deleted')
        
        
    # Close both the SMTP and the IMAP connections
    imap.expunge()
    imap.close()
    
def emailComments(comments, fromEmail):
    """
    TODO:
    
    Detect unsent attachments for this comment and attach them to the comment email
    """
    for x in comments:
        old_date = x.pub_date
        subject = ""
        body = ""
        addrs = []
        services = EmailServices()
        sendEmailFrom = ""
        attachments = [f.__unicode__() for f in x.issue.attachment_set.filter(emailed=False)]
        
        # Subject of email
        issue = x.issue
        if x.commenter.first_name != "Anonymous":
            sendEmailFrom = x.commenter.first_name+" "+x.commenter.last_name+" <"+fromEmail+">"
        else:
            sendEmailFrom = x.commenter.email[0:x.commenter.email.find('@')] + "<"+fromEmail+">"
            
        # Creates the Subject of the email
        subject = x.subject()
        subject = subject.replace('\n', '').replace('\r', '')
            
        # Body of the email
        body = x.comment
        addrs = services.getListOfEmails(x.issue.id, x.only_staff)
        
        # Send the email to the central mail server
        for addr in addrs:
            user = User.objects.get(email=addr).first_name
            if user == "Anonymous":
                body = createCommentTemplateBody(x, False)
            else:
                print "Needs staff User Template"
                body = createCommentTemplateBody(x, True)
            if len(attachments) > 0:
                try:
                    services.sendEmailWithAttachment(sendEmailFrom, addr, subject, body, attachments)
                    for attachment in x.issue.attachment_set.all():
                        attachment.emailed = True
                        attachment.save()
                except Exception, e:
                    print attachments,
                    print e
            else:
                send_mail(subject, body, sendEmailFrom, [addr])
            x.emailed = True
            x.save()

def emailIssues(issues, fromEmail):
    """
    TODO:
    
    Detect unsent attachments for this issue and attach them to the issue email
    """
    for x in issues:
        subject = ""
        body = ""
        addrs = []
        services = EmailServices()
        sendEmailFrom = ""
        addrs = services.getListOfEmails(x.id)
        print "Attempting to get attachments..."
        attachments = [f.__unicode__() for f in x.attachment_set.filter(emailed=False)]
        print "Got attachments...", attachments
        
        # Subject of email
        issue = x
        if x.reporter.first_name != "Anonymous":
            sendEmailFrom = x.reporter.first_name+" "+x.reporter.last_name+" <"+fromEmail+">"
        else:
            sendEmailFrom = x.reporter.email[0:x.reporter.email.find('@')] + "<"+fromEmail+">"
           
        try:
            if len(addrs) > 1:
                addrs.remove(x.reporter.email)
        except:
            print "removing email from addrs did not work..."
            
        print "Got email stuff..."
            
        # Creates the Subject of the email
        subject = x.subject()
        subject = subject.replace('\n', '').replace('\r', '')
            
        print "Got subject..."
            
        # Body of the email
        body = x.description
        
        print "Got body..."
        
        print addrs
        
        # Send the email to the central mail server
        for addr in addrs:
            user = User.objects.get(email=addr).first_name
            if user == "Anonymous":
                print "Needs Anonymous User template"
                body = createIssueTemplateBody(x, False)
            else:
                print "Needs staff User Template"
                body = createIssueTemplateBody(x, True)
            print len(attachments)
            if len(attachments) > 0:
                print "Attachments exist for this issue..."
                try:
                    services.sendEmailWithAttachment(sendEmailFrom, addr, subject, body, attachments)
                    for attachment in x.attachment_set.all():
                        attachment.emailed = True
                        attachment.save()
                except Exception, e:
                    print attachments,
                    print e
            else:
                send_mail(subject, body, sendEmailFrom, [addr])
            x.emailed = True
            x.save()

def emailUpdates(updates, fromEmail):
    for x in updates:
        subject = ""
        body = ""
        addrs = []
        sendEmailFrom = ""
        services = EmailServices()
        
        # Subject of email
        update = x
        if update.acting_user.first_name != "Anonymous":
            sendEmailFrom = update.acting_user.first_name+" "+update.acting_user.last_name+" <"+fromEmail+">"
        else:
            sendEmailFrom = update.acting_user.email[0:update.acting_user.email.find('@')] + "<"+fromEmail+">"
            
        # Creates the Subject of the email
        subject = x.subject()
        subject = subject.replace('\n', '').replace('\r', '')
            
        # Body of the email
        body = x
        addrs = services.getListOfEmails(x.issue.id, True)
        
        try:
            if update.issue.status.name == "Closed":
                addrs.remove(update.issue.reporter.email)
        except Exception, e:
            print e
        
        # Send the email to the central mail server
        for addr in addrs:
            user = User.objects.get(email=addr).first_name
            if user == "Anonymous":
                print "Needs Anonymous User template"
                body = createUpdateTemplateBody(x, False)
            else:
                print "Needs staff User Template"
                body = createUpdateTemplateBody(x, True)
            send_mail(subject, body, sendEmailFrom, [addr])
            x.emailed = True
            x.save()
    
@celery.task(name="tasks.sendIssuesComments")
def sendIssuesComments():
    '''
    Sends an email to the central mail server.
    
    Send emails every 1 minute
    '''
    issues = Issue.objects.filter(emailed=False).order_by('pub_date')
    comments = Comment.objects.filter(emailed=False).order_by('pub_date')
    updates = IssueUpdate.objects.filter(emailed=False).order_by('pub_date')
    fromEmail = EmailServer.objects.get(type="INCOMING").email
    emailComments(comments, fromEmail)
    emailIssues(issues, fromEmail)
    emailUpdates(updates, fromEmail)
    
@celery.task(name="tasks.eventNotifications")
def notifyEventAttendees():
    '''
    '''
    # get events that start tomorrow
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    eventsTomorrow = Event.objects.filter(date=tomorrow)
    fromEmail = EmailServer.objects.get(type="INCOMING").email
    # get each of the event's attendees
    for event in eventsTomorrow:
        attendees = event.attendees
        for attendee in attendees:
            body = createEventReminderEmail(attendee, event)
            subject = "[Arabdicator] Event Reminder"
            send_mail(subject, body, fromEmail, [attendee.email])