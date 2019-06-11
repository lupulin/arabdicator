'''
Created on Oct 21, 2012

@author: Chris Bartos - bartos.25@osu.edu
chrisbartos.com

Models for Project Management
-----------------------------

1. Email functionality -- able to email to a list of users new tasks when sent to a central email address "help@arabidopsis.osu.edu"
2. Multiple Projects -- each project will be the root of a hierarchy of project objects. (projects -have-> (tasks and/or issues))
3. Multiple Tasks -- each project will have multiple tasks (0 to any #)
4. Multiple Issues -- each project will have multiple issues (0 to any #)
5. Multiple Users -- each user can be a "reporter" or a "supervisor"
6. Emailed Issues -- users who email issues will automatically be added to the reporter list. (they will not have access to the web interface, 
                     but will receive emails of comments and whether or not the issue has been resolved or closed).
7. Email servers -- email servers will be customizable. What is important is all necessary information required to connect to mail server.
                 -- mail server will have a "Test Connection" and will output "Connected" if server information is correct, otherwise "Failure".
------------------------------------------------------------------------------------------------------------------------------------------------
7. Each object will accept user comments. You can add a comment via email, or via the web interface
8. Create new users. Email address is required.
9. Each project must have a "supervisor" that controls the project and a list of "reporters" that will report comments/tasks/issues etc.
   Project issues can only be resolved and closed by "supervisor".
   Project tasks can be open only by "supervisor"
   Project tasks can be closed by reporters that are assigned to the task
   Project issues can be opened by anybody via email or web interface.


'''
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.db.models.signals import pre_save, m2m_changed
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from tastypie.models import create_api_key
import datetime

models.signals.post_save.connect(create_api_key, sender=User)

protocol_choices = (("IMAP", "IMAP"),       # IMAP
                    ("SMTP", "SMTP"),       # SMTP
                    ("POP",  "POP"))        # POP
        
emailtypes = (("OUTGOING", "OUTGOING"),     # SMTP
              ("INCOMING", "INCOMING"))     # IMAP / POP

issueTypes = (
    ("Bug", "Bug"),                 # problem which impairs or prevents functions
    ("Improvement", "Improvement"), # an improvement or existing feature
    ("New Feature", "New Feature"), # new feature yet to be developed
    ("Task", "Task"),               # a task that needs to be done
)
class IssueType(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=200, null=True)
    class Meta:
        db_table = u'issuetype'
    def __unicode__(self):
        return self.name

resolutions = (
    ("Fixed", "Fixed"),                       # fixed and tested
    ("Won't Fix", "Won't Fix"),               # problem that won't ever be fixed
    ("Duplicate", "Duplicate"),               # duplicate of an existing issue.
    ("Incomplete", "Incomplete"),             # Not completely described
    ("Cannot Reproduce", "Cannot Reproduce"), # attempts at reproducing issue failed
)
class Resolution(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    class Meta:
        db_table = u'resolution'
    def __unicode__(self):
        return self.name

priorities = (
    ("Blocker",  "Blocker"),  # blocks development
    ("Critical", "Critical"), # crashes, loss of data, memory leak, etc.
    ("Major",    "Major"),    # major loss of function
    ("Minor",    "Minor"),    # minor loss of function
    ("Trivial",  "Trivial"),  # mispelt words
)
class Priority(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=200, blank=True, null=True)
    color = models.CharField(max_length=30)
    class Meta:
        db_table = u'priority'
        
    def __unicode__(self):
        return self.name

statuses = (
    ("Open", "Open"),               # issue is open and ready for assignee to start working
    ("In Progress", "In Progress"), # issue is actively being worked on.
    ("Reopened", "Reopened"),       # issue was once resolved and is now reopened
    ("Resolved", "Resolved"),       # issue has been resolved and is awaiting verification
    ("Closed", "Closed"),           # issue is considered finished / verified by reporter
)
class Status(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    class Meta:
        db_table = u'status'
        
    def __unicode__(self):
        return self.name
        
# Built-in known email servers.
#
# Google, OSU, etc...
class BuiltInEmailConfig(models.Model):
    type = models.CharField(max_length=8, choices=emailtypes)
    hostname = models.CharField(max_length=200)
    protocol = models.CharField(max_length=4, choices=protocol_choices)
    port = models.IntegerField()
    class Meta:
        db_table = u'emailconfigs'
        
# GMail Incoming :
# imap.gmail.com (993) SSL
#
# GMail Outgoing :
# smtp.gmail.com (465 or 587) SSL / TLS
class EmailServer(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    timeout = models.DecimalField(decimal_places=0, max_digits=19, default=300)
    type = models.CharField(max_length=8, choices=emailtypes, default="INCOMING")
    email = models.EmailField(default="help@abrc.osu.edu")
    hostname = models.CharField(max_length=200, default="imap.gmail.com")
    protocol = models.CharField(max_length=4, choices=protocol_choices, default="IMAP")
    port = models.IntegerField(default=993)
    username = models.CharField(max_length=100, default="help@abrc.osu.edu")
    password = models.CharField(max_length=100, default="")
    delete_original = models.BooleanField(default=False)
    class Meta:
        db_table = u'emailserver'
        

# A table used to keep track of users who would like
# access the system.
class InvitedUsers(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField(blank=False)
    accepted = models.BooleanField(default=False)
    class Meta:
        db_table = u'invitedusers'
        
# Activity. Recent Actvity -- used to create activity that
# the system will keep track of:
#    1. Assigned / Reassigned, Open(create) / Resolved / Closed / etc.
#    3. Comment / Event / etc.
class Item(models.Model):
    pub_date = models.DateTimeField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
class Project(models.Model):
    key = models.CharField(max_length=6, unique=True, null=True)
    primary = models.BooleanField(default=False)
    lead = models.ForeignKey(User, null=False)
    name = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True, blank=True)
    item = generic.GenericRelation(Item)
    pub_date = models.DateTimeField(auto_now=True, default=datetime.datetime.now)
    emailed = models.BooleanField(default=True)
    multiplier = models.FloatField(default=0.1)
    class Meta:
        db_table = u'project'
        
    def __unicode__(self):
        return "Project "+self.name+" was created."
    
class Issue(models.Model):
    project = models.ForeignKey(Project, null=False, related_name="issues")
    reporter = models.ForeignKey(User, null=True, related_name="reporter")
    assignees = models.ManyToManyField(User, null=True, related_name="assignees")
    watchers = models.ManyToManyField(User, null=True, related_name="watchers")
    priority = models.ForeignKey(Priority, null=True, default=4)
    resolution = models.ForeignKey(Resolution, null=True, default=6)
    status = models.ForeignKey(Status, null=True, default=1)
    type = models.ForeignKey(IssueType, null=True, default=1)
    name = models.CharField(max_length=300, null=False)
    description = models.TextField(null=True, blank=True)
    description_html = models.TextField(null=True, blank=True)
    emailed = models.BooleanField(default=False)
    pub_date = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)
    last_modified = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)
    last_user = models.ForeignKey(User, null=True)
    item = generic.GenericRelation(Item)
    fixed = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'issue'
        
    def __unicode__(self):
        if self.reporter.first_name == "Anonymous":
            return self.reporter.email + " created issue "+self.project.key+"-"+str(self.pk)
        else:
            return self.reporter.first_name + " " + self.reporter.last_name + " created issue "+self.project.key+"-"+str(self.pk)
    
    def subject(self):
        return "[ABRC HELP]: Created: ("+self.project.key+"-"+str(self.pk)+"): "+ self.name
    
    def save(self, *args, **kwargs):
        self.last_modified = datetime.datetime.now()
        if self.resolution.name == "Fixed":
            self.fixed = datetime.datetime.now()
        else:
            self.fixed = None
        super(Issue, self).save(*args, **kwargs)
    
class Attachment(models.Model):
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now=True)
    issue = models.ForeignKey(Issue, null=True, blank=True)
    emailed = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"/home/cbartos/public/pm/attachments/%s" % self.name
    
class CommentTemplate(models.Model):
    template = models.TextField()
    name = models.CharField(max_length=255)
    
    class Meta:
        db_table = u"commenttemplate"
        
    def __unicode__(self):
        return self.template
    
class Comment(models.Model):
    issue = models.ForeignKey(Issue, null=False, related_name="comments")
    commenter = models.ForeignKey(User, null=False, related_name="comments")
    comment = models.TextField()
    date = models.DateTimeField(default=None)
    emailed = models.BooleanField(default=False)
    item = generic.GenericRelation(Item)
    pub_date = models.DateTimeField(default=None)
    only_staff = models.BooleanField(default=False)
    
    class Meta:
        db_table = u'comment'
        ordering = ["-date"]
        
    def save(self, *args, **kwargs):
        if self.pub_date is None:
            self.pub_date = datetime.datetime.now()
        self.date = datetime.datetime.now()
        super(Comment, self).save(*args, **kwargs)
        
    def subject(self):
        return "[ABRC HELP]: Commented: ("+self.issue.project.key+"-"+str(self.issue.pk)+"): "+ self.issue.name
        
    def __unicode__(self):
        if self.commenter.first_name == "Anonymous":
            return self.commenter.email + " commented on " + self.issue.project.key + "-" + str(self.issue.pk)
        else:
            return self.commenter.first_name + " " + self.commenter.last_name + " commented on " + self.issue.project.key + "-" + str(self.issue.pk)

class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now=False)
    end_date = models.DateTimeField(auto_now=False)
    pub_date = models.DateTimeField(auto_now=True, default=datetime.datetime.now)
    attendees = models.ManyToManyField(User)
    emailed = models.BooleanField(default=False)
    item = generic.GenericRelation(Item)
    class Meta:
        db_table = u'event'
        
    def __unicode__(self):
        localTime = timezone.localtime(self.date)
        return "Event '"+ self.name + "' was created for " + localTime.strftime("%m/%d/%y") + " at " + localTime.strftime("%I:%M %p")
    
class IssueUpdate(models.Model):
    issue = models.ForeignKey(Issue)
    pub_date = models.DateTimeField(auto_now=True, default=datetime.datetime.now)
    acting_user = models.ForeignKey(User, null=True, default=None)
    field = models.CharField(max_length=200)
    oldstring = models.CharField(max_length=40)
    newstring = models.CharField(max_length=40)
    item = generic.GenericRelation(Item)
    emailed = models.BooleanField(default=False)
    class Meta:
        db_table = u'issueupdate'
        
    def __unicode__(self):
        if self.field == "assignee":
            return self.issue.project.key + "-" + str(self.issue.pk) + ": " +self.field + " " + self.oldstring + ": " + self.newstring
        else:
            if self.field == "status":
                return self.acting_user.first_name + " " + self.acting_user.last_name + ": " + self.issue.project.key + "-" + str(self.issue.pk) + " is "+ self.newstring
            else:
                return self.acting_user.first_name + " " + self.acting_user.last_name + ": " + self.issue.project.key + "-" + str(self.issue.pk) + " was updated: "+ self.field+" changed from " + self.oldstring + " to " + self.newstring
 
    def subject(self):
        if self.field == "assignee":
            return "[ABRC HELP]: " + self.oldstring + " assignee: ("+self.issue.project.key+"-"+str(self.issue.pk)+"): "+ self.issue.name
        else:
            if self.field == "status":
                return "[ABRC HELP]: "+ self.newstring + ": ("+self.issue.project.key+"-"+str(self.issue.pk)+"): "+ self.issue.name
            else:
                return "[ABRC HELP]: Updated: ("+self.issue.project.key+"-"+str(self.issue.pk)+"): "+ self.issue.name
 
def update_item(instance, raw, created, **kwargs):
    if created:
        item = Item()
        item.content_type = ContentType.objects.get_for_model(type(instance))
        item.object_id = instance.id
        item.pub_date = instance.pub_date
        item.save()
    else:
        try:
            item = instance.item.all()[0]
            item.save()
        except:
            pass
    
# Create the signals for each type of item
signals.post_save.connect(update_item, IssueUpdate)
signals.post_save.connect(update_item, Event)
signals.post_save.connect(update_item, Issue)
signals.post_save.connect(update_item, Comment)
signals.post_save.connect(update_item, Project)

class MailHandlers(models.Model):
    project = models.ForeignKey(Project)     # default project
    issuetype = models.ForeignKey(IssueType) # default issue type
    reporter = models.ForeignKey(User)       # default reporter
    createusers = models.BooleanField()      # create new users
    notifyusers = models.BooleanField()      # notify users account was created
    
    class Meta:
        db_table = u'mailhandler'
        
class SearchWord(models.Model):
    project = models.ForeignKey(Project)
    word = models.CharField(max_length=40)
    class Meta:
        db_table = u'searchword'
